import fractions
from abc import ABC, abstractmethod
from collections import deque

import av
import numpy as np
from pydub import AudioSegment

TIME_BASE = fractions.Fraction(1, 90000)


class PyAVInterface(ABC):
    @property
    def fps(self):
        return self.stream.base_rate or self.stream.codec_context.framerate

    @property
    def width(self):
        return self.stream.codec_context.width

    @property
    def height(self):
        return self.stream.codec_context.height


class BasePyAVReader(PyAVInterface):
    def __init__(self, path):
        self.container = av.open(path, "r")
        self.stream = next(
            stream for stream in self.container.streams if stream.type == "video"
        )

        codec = None
        if self.stream.codec_context.name == "vp8":
            codec = av.codec.Codec("libvpx", "r")
        elif self.stream.codec_context.name == "vp9":
            codec = av.codec.Codec("libvpx-vp9", "r")
        else:
            codec = av.codec.Codec(self.stream.codec_context.name, "r")

        self.codec = codec
        self.codec_context = codec.create()

        self.buffer = deque()

    @abstractmethod
    def _next(self) -> av.VideoFrame:
        raise NotImplementedError

    def __next__(self):
        return self._next()

    def __iter__(self):
        return self


class PyAVDisposableReader(BasePyAVReader):
    def __init__(self, path, start=0, end=(2 << 62) - 1):
        super().__init__(path)
        self.start = start
        self.end = end

    def _next(self):
        while not self.buffer:
            try:
                packet = next(self.container.demux(self.stream))
                for frame in self.codec_context.decode(packet):
                    if (
                        self.start
                        <= round(frame.pts * self.fps * self.stream.time_base)
                        < self.end
                    ):
                        self.buffer.append(frame)
            except EOFError:
                self.container.close()
                raise StopIteration()
        return self.buffer.popleft()


class PyAVReader(BasePyAVReader):
    @property
    def pts(self):
        if not self.buffer:
            self.buffer.appendleft(self._next())

        return self.buffer[0].pts

    def seek(self, n):
        self.buffer.clear()
        self.container.seek(
            round(n / self.stream.time_base / self.fps), stream=self.stream
        )
        while round(self.pts * self.stream.time_base * self.fps) < n:
            self._next()

    def _next(self):
        while not self.buffer:
            try:
                packet = next(self.container.demux(self.stream))
                for frame in self.codec_context.decode(packet):
                    self.buffer.append(frame)
            except EOFError:
                self.codec_context = self.codec.create()
                self.seek(0)
                raise StopIteration()

        return self.buffer.popleft()


class _Formatter:
    def __init__(self, width: int, height: int, from_pix_fmt: str, to_pix_format: str):
        graph = av.filter.Graph()
        src = graph.add_buffer(
            width=width,
            height=height,
            format=from_pix_fmt,
            time_base=fractions.Fraction(1, 1000),
        )

        reformat = graph.add("format", to_pix_format)
        src.link_to(reformat)

        sink = graph.add("buffersink")
        reformat.link_to(sink)

        graph.configure()

        self.graph = graph

    def __call__(self, frame: av.VideoFrame) -> av.VideoFrame:
        self.graph.push(frame)
        ret = self.graph.pull()
        ret.pts = None
        return ret


class PyAVWriter(PyAVInterface):
    def __init__(
        self,
        path,
        width: int,
        height: int,
        fps: fractions.Fraction,
        *,
        codec_name="libvpx-vp9",
        pix_fmt="yuva420p",
        bit_rate=1024 * 1024,
        alpha_stream=False,
        audio_codec_name=None,
        format=None,
        options={},
    ):
        if codec_name.startswith("libvpx") and alpha_stream:
            pix_fmt = "yuva420p"
            alpha_stream = False

        self.container = av.open(path, "w", format=format, options=options)
        stream = self.container.add_stream(codec_name=codec_name, rate=fps)
        stream.width = width
        stream.height = height
        stream.pix_fmt = pix_fmt
        stream.bit_rate = bit_rate
        stream.time_base = TIME_BASE
        stream.options = options
        self.stream = stream
        self.__frames = 0

        self.alpha_stream = None
        if alpha_stream:
            self.alpha_extractor = AlphaExtractor(width, height)

            alpha_stream = self.container.add_stream(codec_name=codec_name, rate=fps)
            alpha_stream.width = width
            alpha_stream.height = height
            alpha_stream.pix_fmt = "gray"
            alpha_stream.options = options
            self.alpha_stream = alpha_stream

        self.audio_stream = None
        if audio_codec_name is not None:
            audio_stream = self.container.add_stream(
                codec_name=audio_codec_name, rate=48000
            )
            audio_stream.format = "s16"
            audio_stream.layout = "stereo"
            self.audio_stream = audio_stream

    def write(self, array):
        if self.stream.pix_fmt == "yuva420p" or self.alpha_stream is not None:
            frame = av.VideoFrame.from_ndarray(array, format="rgba")
        else:
            frame = av.VideoFrame.from_ndarray(array[..., :3], format="rgb24")

        self.write_video_frame(frame)

    def write_video_frame(self, frame: av.VideoFrame):
        frame.time_base = TIME_BASE
        frame.pts = round(self.__frames / self.fps / frame.time_base)
        self.container.mux(self.stream.encode(frame))

        if self.alpha_stream is not None:
            alpha_frame = self.alpha_extractor(frame)
            if alpha_frame.time_base is not None:
                alpha_frame.pts = round(
                    self.__frames / self.fps / alpha_frame.time_base
                )
            self.container.mux(self.alpha_stream.encode(alpha_frame))

        self.__frames += 1

    def write_audio(self, audio_segment: AudioSegment):
        audio_segment = (
            audio_segment.set_channels(2).set_sample_width(2).set_frame_rate(48000)
        )
        audio_frame = av.AudioFrame.from_ndarray(
            np.array(audio_segment.get_array_of_samples()).reshape(1, -1)
        )
        audio_frame.sample_rate = 48000
        self.container.mux(self.audio_stream.encode(audio_frame))

    def flush(self):
        self.container.mux(self.stream.encode())
        if self.alpha_stream is not None:
            self.container.mux(self.alpha_stream.encode())
        if self.audio_stream is not None:
            self.container.mux(self.audio_stream.encode())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.flush()
        self.container.close()


class Formatter:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.formatters = {
            "yuva420p": _Formatter(width, height, "yuva420p", "rgba"),
            "yuv420p": _Formatter(width, height, "yuva420p", "rgb24"),
        }
        self.ignore = {"rgb24", "rgba"}

    def __call__(self, frame: av.VideoFrame) -> av.VideoFrame:
        if frame.format.name in self.formatters:
            return self.formatters[frame.format.name](frame)
        elif frame.format.name in self.ignore:
            return frame
        else:
            raise NotImplementedError


def to_rgba(reader: BasePyAVReader):
    formatter = Formatter(reader.width, reader.height)
    for frame in reader:
        yield formatter(frame)


def to_array(iterator: list[av.VideoFrame]):
    for frame in iterator:
        yield frame.to_ndarray()


class _AlphaExtractor:
    def __init__(self, width: int, height: int, pix_fmt: str):
        graph = av.filter.Graph()
        src = graph.add_buffer(
            width=width,
            height=height,
            format=pix_fmt,
            time_base=fractions.Fraction(1, 1000),
        )

        alphaextract = graph.add("alphaextract")
        src.link_to(alphaextract)

        alpha = graph.add("buffersink")
        alphaextract.link_to(alpha)

        graph.configure()

        self.graph = graph

    def __call__(self, frame: av.VideoFrame):
        self.graph.push(frame)
        return self.graph.pull()


class AlphaExtractor:
    def __init__(self, width: int, height: int):
        assert height % 2 == 0

        self.rgba = _AlphaExtractor(width, height, "rgba")
        self.yuva420p = _AlphaExtractor(width, int(height * 1.5), "yuva420p")

    def __call__(self, frame: av.VideoFrame):
        if frame.format.name == "rgba":
            return self.rgba(frame)
        elif frame.format.name == "yuva420p":
            return self.yuva420p(frame)
        else:
            raise NotImplementedError


def get_dst_size(dst_size: tuple[int, int], background_image: np.ndarray):
    target_height, target_width = background_image.shape[:2]

    width, height = dst_size
    if target_height / height < target_width / width:
        width = round(target_height / height * width)
        height = target_height
    else:
        height = round(target_width / width * height)
        width = target_width

    width, height = width - width % 16, height - height % 16

    bg_top = (target_height - height) // 2
    bg_left = (target_width - width) // 2

    return (width, height), background_image[
        bg_top : bg_top + height, bg_left : bg_left + width, :
    ]


def get_src_size(
    left: float,
    top: float,
    height: float,
    dst_size: tuple[int, int],
    src_size: tuple[int, int],
):
    dst_width, dst_height = dst_size
    src_width, src_height = src_size

    target_frame_height = dst_height * height
    frame_width = min(
        round(src_width * target_frame_height / src_height),
        dst_width,
    )
    frame_height = round(src_height * frame_width / src_width)

    left = (left + 1) / 2
    left_limit = dst_width - frame_width

    x = round(left * left_limit)
    y = round(top * dst_height)

    return (x, y), (frame_width, frame_height)


class Overlayer:
    def __init__(
        self,
        background_image: np.ndarray,
        dst_size: tuple[int, int],
        src_size: tuple[int, int],
        left=0.0,
        top=0.0,
        height=1.0,
    ):
        origin_src_size = src_size
        dst_size, background_image = get_dst_size(dst_size, background_image)
        src_pos, src_size = get_src_size(left, top, height, dst_size, src_size)

        self.dst_size = dst_size
        self.background_image = av.VideoFrame.from_ndarray(
            background_image, format="rgb24"
        )

        graph = av.filter.Graph()
        src = graph.add_buffer(
            width=origin_src_size[0],
            height=origin_src_size[1],
            format="yuva420p",
            time_base=fractions.Fraction(1, 1000),
        )
        dst = graph.add_buffer(
            width=dst_size[0],
            height=dst_size[1],
            format="rgb24",
            time_base=fractions.Fraction(1, 1000),
        )

        scale = graph.add("scale", f"{src_size[0]}:{src_size[1]}")
        src.link_to(scale)

        overlay = graph.add("overlay", f"{src_pos[0]}:{src_pos[1]}")
        dst.link_to(overlay, input_idx=0)
        scale.link_to(overlay, input_idx=1)

        sink = graph.add("buffersink")
        overlay.link_to(sink)

        graph.configure()

        self.src, self.dst, self.graph = src, dst, graph

    def paste(self, src_image):
        src_image.pts = None
        self.src.push(src_image)
        self.dst.push(self.background_image)

        return self.graph.pull()

    def paste_video(self, iterator: list[av.VideoFrame]):
        for it in iterator:
            yield self.paste(it)
