"""
All this file is currently in 'yta_multimedia' library
because I'm testing it, but the concepts contained in
this file don't belong to this library because they are
related to a VideoEditor concept, not to image or video
simple editing.

We need to handle, when working in building a whole video
project, videos as SubClips so we handle all attributes
and, if we subclip a SubClip instance, we .copy() the
previous attributes to the left, center and right clips
we obtain when subclipping. This would preserve previous
configurations and let us manage all the clips, so we
work on top of moviepy library in any change we process
and use moviepy only for basic and frame transformations.

TODO: These classes below will be moved in a near future
to its own project or to 'youtube_autonomous'.
"""
from yta_multimedia.video.parser import VideoParser
from yta_multimedia.image.edition.image_editor import ImageEditor
from yta_multimedia.video.edition.effect.moviepy.mask import ClipGenerator
from yta_multimedia.video.edition.settings import VOLUME_LIMIT, ZOOM_LIMIT, LAYERS_INDEXES_LIMIT, COLOR_TEMPERATURE_LIMIT, MAX_TIMELINE_LAYER_DURATION, BRIGHTNESS_LIMIT, CONTRAST_LIMIT, WHITE_BALANCE_LIMIT, SHARPNESS_LIMIT
from yta_general_utils.programming.parameter_validator import NumberValidator, PythonValidator
from yta_general_utils.programming.enum import YTAEnum as Enum
from moviepy.Clip import Clip
from moviepy import CompositeVideoClip, concatenate_videoclips
from typing import Union
from copy import deepcopy


END_OF_CLIP = 999999
END_OF_TIMELINE = 120
"""
The limit of the timeline length. It is not possible
to generate a project which length is larger than 
this value.

TODO: This value could be very low in alpha and beta
versions for testing.
"""

# TODO: Move this interval generator to 'yta_general_utils'


# TODO: Move this decorator below to another place (?)
def unset_video_processed(func):
    """
    Decorator function that sets the '_video_processed'
    attribute to None to indicate that it has been
    modified and it must be processed again.
    """
    def wrapper(self, value):
        value = func(self, value)
        self._video_processed = None
        
        return value
    
    return wrapper


from yta_general_utils.math.rate_functions import mRateFunction
from yta_general_utils.math.progression import Progression

class VideoSetting:
    """
    Class to represent a video setting to be able to handle
    dynamic setting values and not only simple values. This
    means we can make a video go from 0 contrast to 10 
    contrast increasing it smoothly (for example: 0, 2, 4,
    6, 8 and 10) and not only abruptly (from 0 in one frame
    to 10 in the next frame).
    """
    initial_value: float = None
    final_value: float = None
    rate_function: mRateFunction = None

    def __init__(self, initial_value: float, final_value: float, rate_function: mRateFunction = mRateFunction.LINEAR):
        # TODO: Maybe validate something? I don't know the
        # limits because each setting is different, but by
        # now I'm verifying the 'initial_value' and the
        # 'final_value' when using them on a SubClip
        self.initial_value = initial_value
        self.final_value = final_value
        self.rate_function = rate_function

    def get_values(self, steps: int):
        """
        Obtain an array with the values between the 'initial_value'
        and the 'final_value' according to the 'rate_function'.

        The 'steps' parameter must be the amount of frames in which
        we are planning to apply this setting so we are able to read
        the value for each frame according to its index.
        """
        # Same limits cannot be handled by the Progression class as
        # it is just an array of the same value repeated 'steps' 
        # times
        if self.initial_value == self.final_value:
            return [self.initial_value for _ in range(steps)]
        
        # TODO: Think a new way to avoid calculating the progression
        # again and again when asking for the same amount of 'steps'
        # and attributes are still the same
        return Progression(self.initial_value, self.final_value, steps, self.rate_function).values
    
    def copy(self):
        return VideoSetting(
            self.initial_value,
            self.final_value,
            self.rate_function
        )

class SubClip:
    """
    Class to represent a subclip of a clip in which we
    can apply different modifications such as color
    temperature, zoom, movement, etc.

    This class represent the same as one of the subclips
    in any of your video editor apps.
    """
    # TODO: This, as the original video clip (moviepy),
    # maybe must be private to avoid using it directly
    video: Clip = None
    _video_processed: Clip = None
    """
    The video once it's been processed with all its
    attributes and effects.
    """
    # TODO: Add all needed attributes
    # Volume
    _volume: int = None
    # Color attributes
    _color_temperature: VideoSetting = None
    _color_temperature_values: list[float] = None
    """
    A list of values for the color temperature modification
    in which each position is the modifier for each video
    frame.
    """
    _brightness: VideoSetting = None
    _brightness_values: list[float] = None
    """
    A list of values for the brightness modification in
    which each position is the modifier for each video
    frame.
    """
    _contrast: VideoSetting = None
    _contrast_values: list[float] = None
    """
    A list of values for the contrast modification in which
    each position is the modifier for each video frame.
    """
    _sharpness: VideoSetting = None
    _sharpness_values: list[float] = None
    """
    A list of values for the sharpness modification in which
    each position is the modifier for each video frame.
    """
    _white_balance: VideoSetting = None
    _white_balance_values: list[float] = None
    """
    A list of values for the white balance modification in
    which each position is the modifier for each video frame.
    """
    # Zoom and movement
    _zoom: int = None
    x_movement: int = None
    y_movement: int = None
    rotation: int = None
    # Custom effects
    _effects: list['MEffect'] = None

    @staticmethod
    def init(video: Clip, start_time: Union[float, None] = 0, end_time: Union[float, None] = END_OF_CLIP):
        """
        This is the only method we need to use when instantiating
        a SubClip so we can obtain the left and right clip result
        of the subclipping process and also the new SubClip
        instance.

        This method returns a tuple with 3 elements, which are the
        left part of the subclipped video, the center part and the
        right part as SubClip instances. If no left or right part,
        they are return as None. So, the possibilities are (from
        left to right):

        - SubClip, SubClip, SubClip
        - SubClip, SubClip, None
        - None, SubClip, SubClip
        - None, SubClip, SubClip
        """
        video = VideoParser.to_moviepy(video)

        left_clip, center_clip, right_clip = subclip_video(video, start_time, end_time)

        return (
            SubClip(left_clip) if left_clip is not None else None,
            SubClip(center_clip),
            SubClip(right_clip) if right_clip is not None else None
        )

    def __init__(self, video: Clip):
        """
        DO NOT USE THIS METHOD DIRECTLY. Use static '.init()'
        method instead.

        The SubClip instantiating method has to be called only
        in the static 'init' method of this class so we are able
        to handle the rest of the clips (if existing) according
        to the subclipping process we do.
        """
        self.video = VideoParser.to_moviepy(video)
        self.volume = 100

    @property
    def video_processed(self):
        if not self._video_processed:
            self._video_processed = self._process()

        return self._video_processed

    @property
    def duration(self):
        """
        Shortcut to the actual duration of the video once
        it's been processed.
        """
        # TODO: Maybe this has to be the pre-processed
        #return self.video_processed.duration
        return self.video.duration
    
    @property
    def size(self):
        """
        Shortcut to the actual size of the video once
        it's been processed.
        """
        # TODO: Maybe this has to be the pre-processed
        return self.video_processed.size
    
    @property
    def fps(self):
        """
        Fps of the original video (the pre-processed one).
        """
        return self.video.fps
    
    @property
    def number_of_frames(self):
        """
        Number of frames of the original video (the 
        pre-processed one).

        Due to a bug with the moviepy reading way, this
        number cannot be the real number. Check the 
        MPVideo class that looks for the exact number.
        """
        return int(self.duration * self.fps + 0.000001)
    
    @property
    def zoom(self):
        return self._zoom
    
    @zoom.setter
    @unset_video_processed
    def zoom(self, value):
        _validate_zoom(value)
        
        self._zoom = int(value)

    @property
    def color_temperature(self):
        return self._color_temperature
    
    @color_temperature.setter
    @unset_video_processed
    def color_temperature(self, value: VideoSetting):
        _validate_color_temperature(value)

        # TODO: I think we don't need the VideoSetting
        self._color_temperature = value
        self._color_temperature_values = value.get_values(self.number_of_frames)

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    @unset_video_processed
    def brightness(self, value: VideoSetting):
        _validate_brightness(value)

        # TODO: I think we don't need the VideoSetting
        self._brightness = value
        self._brightness_values = value.get_values(self.number_of_frames)

    @property
    def contrast(self):
        return self._contrast
    
    @contrast.setter
    @unset_video_processed
    def contrast(self, value: VideoSetting):
        _validate_contrast(value)

        # TODO: I think we don't need the VideoSetting
        self._contrast = value
        self._contrast_values = value.get_values(self.number_of_frames)

    @property
    def sharpness(self):
        return self._sharpness
    
    @sharpness.setter
    @unset_video_processed
    def sharpness(self, value: VideoSetting):
        _validate_sharpness(value)

        # TODO: I think we don't need the VideoSetting
        self._sharpness = value
        self._sharpness_values = value.get_values(self.number_of_frames)

    @property
    def white_balance(self):
        return self._white_balance
    
    @white_balance.setter
    @unset_video_processed
    def white_balance(self, value: VideoSetting):
        _validate_white_balance(value)

        # TODO: I think we don't need the VideoSetting
        self._white_balance = value
        self._white_balance_values = value.get_values(self.number_of_frames)

    @property
    def volume(self):
        return self._volume
    
    @volume.setter
    @unset_video_processed
    def volume(self, value):
        _validate_volume(value)
        
        self._volume = int(value)

    @property
    def effects(self):
        return self._effects
    
    @effects.setter
    @unset_video_processed
    def effects(self, value):
        """
        Add a list of custom effects instances to apply on the clip.

        TODO: Is this interesting, or maybe just a method to add them
        one by one (?)
        """
        # TODO: Do we validate anything else than below (?)
        #_validate_effect(value)

        if PythonValidator.is_list(value) and any(not PythonValidator.is_subclass(value, 'MEffect')):
            raise Exception('Some of the given effects in "value" parameter are not MEffect subclass instances.')

        self._effects = value

    def set_color_temperature(self, start: int, end: Union[int, None] = None, rate_function: mRateFunction = mRateFunction.LINEAR):
        """
        Set a new color temperature that will be modified frame by frame.

        If only 'start' is provided, the change will be the same in all
        frames, but if a different 'end' value is provided, the also given
        'rate_function' will be used to calculate the values in between
        those 'start' and 'end' limits to be applied in the corresponding
        frames.
        """
        self.color_temperature = VideoSetting(start, start if end is None else end, mRateFunction.to_enum(rate_function))

    def set_brightness(self, start: int, end: Union[int, None] = None, rate_function: mRateFunction = mRateFunction.LINEAR):
        """
        Set a new brightness that will be modified frame by frame.
        
        If only 'start' is provided, the change will be the same in all
        frames, but if a different 'end' value is provided, the also given
        'rate_function' will be used to calculate the values in between
        those 'start' and 'end' limits to be applied in the corresponding
        frames.
        """
        self.brightness = VideoSetting(start, start if end is None else end, mRateFunction.to_enum(rate_function))

    def set_contrast(self, start: int, end: Union[int, None] = None, rate_function: mRateFunction = mRateFunction.LINEAR):
        """
        Set a new contrast that will be modified frame by frame.
        
        If only 'start' is provided, the change will be the same in all
        frames, but if a different 'end' value is provided, the also given
        'rate_function' will be used to calculate the values in between
        those 'start' and 'end' limits to be applied in the corresponding
        frames.
        """
        self.contrast = VideoSetting(start, start if end is None else end, mRateFunction.to_enum(rate_function))

    def set_sharpness(self, start: int, end: Union[int, None] = None, rate_function: mRateFunction = mRateFunction.LINEAR):
        """
        Set a new sharpness that will be modified frame by frame.
        
        If only 'start' is provided, the change will be the same in all
        frames, but if a different 'end' value is provided, the also given
        'rate_function' will be used to calculate the values in between
        those 'start' and 'end' limits to be applied in the corresponding
        frames.
        """
        self.sharpness = VideoSetting(start, start if end is None else end, mRateFunction.to_enum(rate_function))

    def set_white_balance(self, start: int, end: Union[int, None] = None, rate_function: mRateFunction = mRateFunction.LINEAR):
        """
        Set a new white balance that will be modified frame by frame.
        
        If only 'start' is provided, the change will be the same in all
        frames, but if a different 'end' value is provided, the also given
        'rate_function' will be used to calculate the values in between
        those 'start' and 'end' limits to be applied in the corresponding
        frames.
        """
        self.white_balance = VideoSetting(start, start if end is None else end, mRateFunction.to_enum(rate_function))

    def add_effect(self, effect: 'MEffect'):
        """
        Add the provided 'effect' instance to be applied on the clip.
        """
        if not PythonValidator.is_an_instance(effect) or not PythonValidator.is_subclass(effect, 'MEffect'):
            raise Exception('The provided "effect" parameter is not an instance of a MEffect subclass.')
        
        # TODO: Check that effect is valid (times are valid, there is
        # not another effect that makes it incompatible, etc.)
        self._effects.append(effect)

    def subclip(self, start: float, end: float):
        """
        This method will split the current SubClip instance
        into 3 different items, that will be new instances
        of SubClip class according to the 'start' and 'end'
        times provided.

        This method uses a copy of the current instance to
        not modify it but returning completely new (by
        using deepcopy). All settings and effects will be
        preserved as they were in the original instance for
        all of the new copies.

        This method will return 3 values: left part of the
        SubClip, center part and right part. Left and right
        part can be None.
        """
        # TODO: Validate
        if not NumberValidator.is_positive_number(start):
            raise Exception('The "start" parameter provided is not a valid and positive number (0 included).')
        
        if not NumberValidator.is_positive_number(end):
            raise Exception('The "end" parameter provided is not a valid and positive number (0 included).')
        
        if start >= end:
            raise Exception('The "start" parameter provided is greater or equal than the "end" parameter provided.')
        
        if end > self.duration:
            raise Exception(f'The "end" provided ({end}s) is longer than the current video duration ({self.duration}s).')

        # TODO: I need to calculate the frame index in which I'm
        # splitting the subclip to also subclip the arrays that
        # are inside the instance
        left = self.copy() if start not in (None, 0) else None
        center = self.copy()
        right = self.copy() if end is not None and end < self.duration else None

        def replace_attribute_values(instance, start_index: Union[float, None], end_index: Union[float, None]):
            def split_array(array: list, start_index: Union[float, None], end_index: Union[float, None]):
                # TODO: Validate 'start_index' and 'end_index' according
                # to 'array' size
                if start_index is not None and end_index is not None: return array[start_index:end_index]
                if start_index is not None: return array[start_index:]
                if end_index is not None: return array[:end_index]
                return array

            # TODO: Append here any new array of values per frame
            instance._color_temperature_values = split_array(instance._color_temperature_values, start_index, end_index) if instance._color_temperature_values is not None else None
            instance._brightness_values = split_array(instance._brightness_values, start_index, end_index) if instance._brightness_values is not None else None
            instance._contrast_values = split_array(instance._contrast_values, start_index, end_index) if instance._contrast_values is not None else None
            instance._sharpness_values = split_array(instance._sharpness_values, start_index, end_index) if instance._sharpness_values is not None else None
            instance._white_balance_values = split_array(instance._white_balance_values, start_index, end_index) if instance._white_balance_values is not None else None
            
            return instance

        last_index = 0
        # Left
        if left is not None:
            left.video = left.video.with_subclip(0, start)
            last_index = left.number_of_frames
            # Modify all the attributes per frame values
            replace_attribute_values(left, last_index, None)

        # Center
        center.video = center.video.with_subclip(start, end)
        # Modify all the attributes per frame values
        replace_attribute_values(center, last_index, last_index + center.number_of_frames)
        last_index = last_index + center.number_of_frames

        # Right
        if right is not None:
            right.video = right.video.with_subclip(start_time = end)
            # Modify all the attributes per frame values
            replace_attribute_values(right, None, last_index)

        return left, center, right
    
    def _process(self):
        """
        Process the video clip with the attributes set and 
        obtain a copy of the original video clip with those
        attributes and effects applied on it. This method
        uses a black (but transparent) background with the
        same video size to make sure everything works 
        properly.

        This method doesn't change the original clip, it
        applies the changes on a copy of the original one
        and returns that copy modified.
        """
        video = self.video.copy()
        black_background_video = ClipGenerator.get_default_background_video(duration = video.duration)

        from yta_multimedia.video import MPVideo

        # I use this class to ensure it fits the real number
        # of frames so we can modify it correctly
        video_handler = MPVideo(video)

        # TODO: The 3 customizable elements
        # This can be a factor or an absolute value, but I
        # recommend being a factor because it is easier
        resizes = [1 for _ in video_handler.frames_time_moments]
        rotations = [0 for _ in video_handler.frames_time_moments]
        # Position must be, at first, a center position, and then
        # transformed into upper left corner position to be 
        # positioned
        positions = [('center', 'center') for _ in video_handler.frames_time_moments]

        # Functions that need to be processed frame by frame
        def modify_video_frame_by_frame(get_frame, t):
            """
            Modificate anything related to pixel colors, distortion,
            etc. and not to position, rotation or frame size.
            """
            frame = get_frame(t)
            frame_index = video_handler.frame_time_to_frame_index(t, video.fps)

            frame = ImageEditor.modify_color_temperature(frame, self._color_temperature_values[frame_index]) if self.color_temperature is not None else frame
            frame = ImageEditor.modify_brightness(frame, self._brightness_values[frame_index]) if self.brightness is not None else frame
            frame = ImageEditor.modify_contrast(frame, self._contrast_values[frame_index]) if self.contrast is not None else frame
            frame = ImageEditor.modify_sharpness(frame, self._sharpness_values[frame_index]) if self.sharpness is not None else frame
            frame = ImageEditor.modify_white_balance(frame, self._white_balance_values[frame_index]) if self.white_balance is not None else frame

            return frame
        
        # Apply frame by frame video modifications
        video = video.transform(lambda get_frame, t: modify_video_frame_by_frame(get_frame, t))

        # Functions that can be processed in the whole clip
        # TODO: Careful. Some of these modification can be
        # done before the video positioning or resizing, so
        # the behaviour could be unexpected.
        size = video.size
        if self.zoom is not None:
            size = (self.zoom / 100 * size[0], self.zoom / 100 * size[1])
        
            video = video.resized(size)
            # This is to force the size to be 1920x1080 instead
            # of other bigger values, but thiss does not make 
            # the clip render faster
            # from moviepy.video.fx.Crop import Crop
            # video = Crop(x_center = video.size[0] / 2, y_center = video.size[1] / 2, width = 1920, height = 1080).apply(video)

        # Apply position, rotation and resize frame by frame
        video = video.resized(lambda t: resizes[video_handler.frame_time_to_frame_index(t, video_handler.fps)])
        video = video.with_position(lambda t: positions[video_handler.frame_time_to_frame_index(t, video_handler.fps)])
        # TODO: There is a Rotate Effect for rotating... so we could
        # use it instead of this (?)
        video = video.rotated(lambda t: rotations[video_handler.frame_time_to_frame_index(t, video_handler.fps)])

        # Functions that changes the audio
        if self.volume != 100:
            video = video.with_volume_scaled(self.volume / 100)

        # TODO: This below is repeated in VideoEditor class as
        # '._overlay_video()'
        return CompositeVideoClip([
            black_background_video,
            video
        ])#.with_audio(VideoAudioCombinator(audio_mode).process_audio(background_video, video))
    
    def copy(self):
        # TODO: Complete this method to manually copy the instance
        # because 'deepcopy' is not working properly
        copy = SubClip(self.video.copy())
        copy.color_temperature = self.color_temperature.copy() if self.color_temperature is not None else None
        copy._color_temperature_values = self._color_temperature_values.copy() if self._color_temperature_values is not None else None
        copy.brightness = self.brightness.copy() if self.brightness is not None else None
        copy._brightness_values = self._brightness_values.copy() if self._brightness_values is not None else None
        copy.contrast = self.contrast.copy() if self.contrast is not None else None
        copy._contrast_values = self._contrast_values.copy() if self._contrast_values is not None else None
        copy.sharpness = self.sharpness.copy() if self.sharpness is not None else None
        copy._sharpness_values = self._sharpness_values.copy() if self._sharpness_values is not None else None
        copy.white_balance = self.white_balance.copy() if self.white_balance is not None else None
        copy._white_balance_values = self._white_balance_values.copy() if self._white_balance_values is not None else None

        return copy

class SubClipOnTimelineLayer:
    """
    Class to represent one of our SubClips but in
    the general project timeline and in a specific
    layer of it, with the start and end moment in
    that timeline, and also the layer in which it
    is placed.

    TODO: This is a concept in test phase. SubClip
    is a more definitive concept.
    """
    subclip: SubClip = None
    start_time: float = None
    """
    The start time on the general project timeline. Do 
    not confuse this term with the start time of a
    moviepy clip.
    """

    @property
    def video_processed(self):
        return self.subclip.video_processed

    @property
    def duration(self):
        """
        Shortcut to the actual duration of the video once
        it's been processed.
        """
        return self.subclip.duration
    
    @property
    def size(self):
        """
        Shortcut to the actual size of the video once it's
        been processed.
        """
        return self.subclip.size
    
    @property
    def end_time(self):
        """
        The end moment on the timeline, based on this
        instance 'start_time' and the real video 'duration'.
        """
        return self.start_time + self.duration

    def __init__(self, subclip: SubClip, start_time: float):
        if not PythonValidator.is_instance(subclip, SubClip):
            raise Exception('The provided "subclip" parameter is not a valid SubClip instance.')
        
        if not NumberValidator.is_number_between(start_time, 0, END_OF_TIMELINE):
            raise Exception(f'The provided "start_time" parameter is not a valid number between in the range (0, {END_OF_TIMELINE})')
        
        self.subclip = subclip
        self.start_time = start_time

    # def _process(self):
    #     return self.subclip._process()

class TimelineLayerType(Enum):
    """
    The type of a timeline layer, which will determine
    which kind of SubClips are accepted by the layer
    with this type.
    """
    VIDEO = 'video'
    """
    The type of layer that only accept video SubClips.
    """
    AUDIO = 'audio'
    """
    The type of layer that only accept audio SubClips.
    """
    # TODO: Probably add 'GreenscreenLayer',
    # 'AlphascreenLayer', 'TextLayer', 'SubtitleLayer',
    # and all needed in a future when this concept 
    # evolves properly

class TimelineLayer:
    index: int = None
    type: TimelineLayerType = None
    _subclips: list[SubClipOnTimelineLayer] = None

    @property
    def subclips(self):
        """
        The list of subclips in this timeline layer, ordered
        according to its 'start_time' from first to be displayed
        to last ones.
        """
        return sorted(self._subclips, key = lambda subclip: subclip.start_time)
    
    @property
    def duration(self):
        """
        The duration of this timeline layer, which is the
        'end_time' of the last displayed subclip, or 0 if no
        clips.
        """
        return self.subclips[-1].end_time if self.subclips else 0
    
    @property
    def all_clips(self):
        """
        The list of all clips needed to fulfill the timeline
        layer completely. This involves the actual subclips
        but also the needed black background clips to put in
        the gaps between the subclips.
        """
        all_subclips = []
        current_time_moment = 0
        # TODO: This 'timeline_duration' must be calculated
        # according to all timeline layers, so the longest
        # one is the one we need to assign here
        timeline_duration = self.subclips[-1].end_time

        for subclip in self.subclips:
            # We fulfill the gap if existing
            if subclip.start_time > current_time_moment:
                all_subclips.append(ClipGenerator.get_default_background_video(subclip.size, subclip.start_time - current_time_moment))
            
            # We add the existing subclip
            all_subclips.append(subclip.video_processed)
            
            current_time_moment = subclip.end_time
        
        # Check if gap at the end due to other longer layers
        if current_time_moment < timeline_duration:
            all_subclips.append(ClipGenerator.get_default_background_video(subclip.size, timeline_duration - current_time_moment))
        
        return all_subclips

    def __init__(self, index: int = 0, type: TimelineLayerType = TimelineLayerType.VIDEO):
        _validate_layer_index(index)
        type = TimelineLayerType.to_enum(type) if type is not None else TimelineLayerType.VIDEO

        self.index = index
        self.type = type
        self._subclips = []

    def add_subclip(self, subclip: SubClip, start_time: float):
        """
        Append the provided 'subclip' at the end of the list.

        TODO: Being in the end of the list doesn't mean being
        the last one displayed. By now I'm storing them just
        one after another and ordering them when trying to get
        them as a property. This will change in a near future
        to be more eficient.
        """
        if not PythonValidator.is_instance(subclip, SubClip):
            raise Exception('The provided "subclip" parameter is not a valid instance of the SubClip class.')
        
        if not NumberValidator.is_number_between(start_time, 0, MAX_TIMELINE_LAYER_DURATION):
            raise Exception('The provided "start_time" is not a valid value')

        # 
        # TODO: Check that the 'start_time' or the 'duration'
        # doesn't collide with another existing subclip. If
        # yes, choose what strategy to follow
        if any(subclip.start_time <= start_time <= subclip.end_time for subclip in self.subclips):
            raise Exception(f'There is one existing subclip at the {str(start_time)} time position.')

        self._subclips.append(SubClipOnTimelineLayer(subclip, start_time))

    def remove_subclip(self, index: int):
        """
        Delete the subclip in the provided 'index' position of
        the list (if existing), or raises an Exception if it
        doesn't exist or the list is empty.
        """
        # TODO: Maybe remove by passing the instance (?)
        if PythonValidator.is_empty_list(self._subclips):
            # TODO: Maybe I should not raise an Exception here...
            raise Exception('No subclips to remove.')
        
        if not NumberValidator.is_number_between(0, len(self._subclips)):
            raise Exception(f'The provided "index" is not a valid index (must be between [0, {str(len(self._subclips))}).')

        # TODO: Be very careful, I have a 'subclips' property which
        # returns the subclips ordered, but the raw '_subclips'
        # property is not ordered, so here the 'index' is potentially
        # wrong. Think how to handle this in a near future, please.
        del self._subclips[index]

    def build(self):
        """
        Concatenate all the timeline layer subclips (fulfilling the
        gaps with black transparent background clips) and return the
        concatenated clip.
        """
        # TODO: What if I have one non-transparent and transparent
        # clips in this timeline layer? They will be treated in a
        # similar way so it is not the expected behaviour...
        return concatenate_videoclips(self.all_clips)
    
class VideoProject:
    """
    Class representing a whole but single video project
    in which we have a timeline with different layers
    and clips on them.
    """
    timeline_layers: list[TimelineLayer] = None
    screen_size: tuple[int, int] = None
    """
    Dimensions of the final video that has to be
    exported.
    """

    def __init__(self, screen_size: tuple[int, int] = (1920, 1080)):
        self.timeline_layers = [
            TimelineLayer(0, TimelineLayerType.VIDEO),
            # TODO: I Simplify everything by now and I only
            # handle one video layer
            #TimelineLayer(0, TimelineLayerType.AUDIO)
        ]
        # TODO: Validate 'screen_size'
        self.screen_size = screen_size

    def get_layers(self, type: TimelineLayerType) -> list[TimelineLayer]:
        """
        Get the timeline layers of the provided 'type' sorted by
        index in ascending order.
        """
        type = TimelineLayerType.to_enum(type)

        return sorted(
            [layer for layer in self.timeline_layers if layer.type == type], 
            key = lambda layer: layer.index
        )
    
    def get_last_layer_index(self, type: TimelineLayerType) -> Union[int, None]:
        """
        Get the last index used for the layers of the given
        'type', that will be None if no layers of that type.
        """
        type = TimelineLayerType.to_enum(type)

        layers = self.get_layers(type)

        return layers[-1:].index if not PythonValidator.is_empty_list(layers) else None

    def add_layer(self, type: TimelineLayerType = TimelineLayerType.VIDEO) -> int:
        """
        Add a new layer of the provided 'type' and returns
        the index in which it has been placed.
        """
        type = TimelineLayerType.to_enum(type) if type is not None else TimelineLayerType.VIDEO

        layers = self.get_layers(type)
        index = len(layers) + 1 if layers else 0

        self.timeline_layers.append(TimelineLayer(index, type))

        return index
    
    def remove_layer(self, layer: TimelineLayer):
        if not PythonValidator.is_instance(layer, TimelineLayer):
            raise Exception('The provided "layer" is not an instance of the TimelineLayer class.')
        
        if layer not in self.timeline_layers:
            raise Exception('The provided "layer" does not exist in this project.')

        self.timeline_layers.remove(layer)

    def build(self):
        from yta_multimedia.video.edition.duration import set_video_duration, ExtendVideoMode
        # TODO: Remove this code below when this is done 
        # individually by each layer. By now I'm forcing
        # all layers clips to have the same duration as
        # the longest layer clip has, but must be done
        # using a general and common 'max_duration'
        # property that is not calculated here.
        layers_clips = [
            layer.build()
            for layer in self.timeline_layers
        ]
        # TODO: Omg, cyclic import issue here again...
        max_duration = max(layer_clip.duration for layer_clip in layers_clips)
        layers_clips = [
            set_video_duration(layer_clip, max_duration, extend_mode = ExtendVideoMode.BLACK_TRANSPARENT_BACKGROUND)
            for layer_clip in layers_clips
        ]

        return CompositeVideoClip(layers_clips)





def subclip_video(video: Clip, start_time: float, end_time: float) -> tuple[Union[Clip, None], Clip, Union[Clip, None]]:
    """
    Subclip the provided 'video' into 3 different subclips,
    according to the provided 'start_time' and 'end_time',
    and return them as a tuple of those 3 clips. First and
    third clip could be None.

    The first clip will be None when 'start_time' is 0, and 
    the third one when the 'end_time' is equal to the given
    'video' duration.
    """
    video = VideoParser.to_moviepy(video)

    left = None if (start_time == 0 or start_time == None) else video.with_subclip(0, start_time)
    center = video.with_subclip(start_time, end_time)
    right = None if (end_time is None or end_time >= video.duration) else video.with_subclip(start_time = end_time)

    return left, center, right



# TODO: This must be maybe moved to another file
# because it is mixed with the 'subclip_video'
# method...
def _validate_layer_index(layer_index: int):
    if not NumberValidator.is_number_between(layer_index, LAYERS_INDEXES_LIMIT[0], LAYERS_INDEXES_LIMIT[1]):
        raise Exception(f'The provided "layer_index" is not a valid layer, it must be an int value between [{LAYERS_INDEXES_LIMIT[0]}, {LAYERS_INDEXES_LIMIT[1]}].')
    
def _validate_zoom(zoom: int):
    if not NumberValidator.is_number_between(zoom, ZOOM_LIMIT[0], ZOOM_LIMIT[1]):
        raise Exception(f'The "zoom" parameter provided is not a number between [{ZOOM_LIMIT[0]}, {ZOOM_LIMIT[1]}].')
    
def _validate_color_temperature(color_temperature: VideoSetting):
    _validate_setting(color_temperature, 'color_temeprature', COLOR_TEMPERATURE_LIMIT)
    
def _validate_brightness(brightness: VideoSetting):
    _validate_setting(brightness, 'brightness', BRIGHTNESS_LIMIT)

def _validate_contrast(contrast: VideoSetting):
    _validate_setting(contrast, 'contrast', CONTRAST_LIMIT)

def _validate_sharpness(sharpnes: VideoSetting):
    _validate_setting(sharpnes, 'sharpness', SHARPNESS_LIMIT)
    
def _validate_white_balance(white_balance: VideoSetting):
    _validate_setting(white_balance, 'white_balance', WHITE_BALANCE_LIMIT)
    
def _validate_setting(setting: VideoSetting, name: str, range: tuple[float, float]):
    if not PythonValidator.is_instance(setting, VideoSetting):
        raise Exception(f'The provided "{name}" is not a VideoSetting instance.')
    
    if not NumberValidator.is_number_between(setting.initial_value, range[0], range[1]):
        raise Exception(f'The "{name}" parameter provided "initial_value" is not a number between [{range[0]}, {range[1]}].')
    
    if not NumberValidator.is_number_between(setting.final_value, range[0], range[1]):
        raise Exception(f'The "{name}" parameter provided "final_value" is not a number between [{range[0]}, {range[1]}].')

def _validate_volume(volume: int):
    if not NumberValidator.is_number_between(volume, VOLUME_LIMIT[0], VOLUME_LIMIT[1]):
        raise Exception(f'The "volume" parameter provided is not a number between [{VOLUME_LIMIT[0]}, {VOLUME_LIMIT[1]}].')