from ..types import Precursor, UnknownLength, Widget as WidgetType, CustomRender as CustomRenderType
from .abc import Widget, CustomRender, WidgetWrapper
from .._features.precursor import Precursor as PrecursorFeature
from ....tools.terminal import Color as _color
from ....typing import override
from threading import Thread
from typing import Union, Tuple
import datetime

PrecursorError = Precursor.PrecursorError
Color = _color

class Label(Widget):
    __name__: str = 'Label'

    def __init__(
            self,
            label: str = 'Loading',
            separator: str = ':',
    ) -> None:

        self.label = label
        self.separator = separator
        self._precursor: Precursor = None
        self._length = len(label) + len(separator)

    @property
    def precursor(self) -> Precursor:
        raise PrecursorError(PrecursorError.NOT_NEEDED)
    
    @precursor.setter
    def precursor(self, precur: Precursor) -> None:
        raise PrecursorError(PrecursorError.NOT_NEEDED)
    
    @precursor.deleter
    def precursor(self) -> None:
        raise PrecursorError(PrecursorError.NOT_NEEDED)
    
    def render(self) -> str:
        return self.label + self.separator
    
    @property
    def length(self) -> Union[int, UnknownLength]:
        return self._length
    
    @property
    def thread(self) -> Thread:
        raise PrecursorError(PrecursorError.NOT_NEEDED)
    
    @property
    def is_sensitive(self) -> bool:
        return False

class Bar(CustomRender, PrecursorFeature):
    __name__: str = 'Bar'

    def __init__(
            self,
            finished_marker: str = '█',
            unfinished_marker: str = '░',
            start_marker: str = '|',
            end_marker: str = '|'
    ) -> None:
        
        self.finished_marker = finished_marker
        self.unfinished_marker = unfinished_marker
        self.start_marker = start_marker
        self.end_marker = end_marker
        self._precursor: Precursor = None
        self._length: int = None
        self._possible_length = 0
        self._normalization = 100
    
    def set_possible_length(self, length: float) -> None:
        self._possible_length = length - len(self.start_marker) - len(self.end_marker)
    
    def set_normalization(self, normalization: float) -> None:
        self._normalization = normalization
    
    @property
    def precursor(self) -> Precursor:
        if self._precursor is None:
            raise PrecursorError(PrecursorError.PRECURSOR_PROPERTY)
        return self._precursor
    
    @precursor.setter
    def precursor(self, precur: Precursor) -> None:
        if not isinstance(precur, Precursor):
            raise PrecursorError(PrecursorError.PRECURSOR_INSTANCE.format('precursor'))
        self._precursor = precur
    
    @precursor.deleter
    def precursor(self) -> None:
        raise PrecursorError(PrecursorError.PRECURSOR_DELETE)
    
    @property
    def length(self) -> Union[int, UnknownLength]:
        return UnknownLength() if self._length is None else self._length
    
    @property
    def is_sensitive(self) -> bool:
        return False
    
    @property
    def thread(self) -> Thread:
        if self._precursor is None:
            raise PrecursorError(PrecursorError.PRECURSOR_THREAD)
        return self.precursor.threads.get(self.__name__, None)
    
    def render(self) -> str:
        # Make sure precursor is available.
        if self._precursor is None:
            raise PrecursorError(PrecursorError.WIDGET_RENDER.format(self.__name__))

        # normalize the bar length if normalization is less than 100
        if self._normalization < 100:
            possible_length = int((self._possible_length/100)*self._normalization)
        else:
            possible_length = int(self._possible_length)
        
        self.finished = int((self.precursor.percent/100) * possible_length)
        self.unfinished = possible_length - self.finished

        bar = self.finished_marker * self.finished + self.unfinished_marker * self.unfinished
        barstate = self.start_marker + bar + self.end_marker

        self._length = len(barstate)
        return barstate

class Time(Widget, PrecursorFeature):
    __name__: str = 'Time'

    def __init__(self, format: str = 'Elapsed Time: {}') -> None:
        self.format = format
        self._precursor: Precursor = None
        self._length = len(format.format('HH:MM:SS'))
    
    @staticmethod
    def normalize_time(seconds: float) -> str:
        return str(datetime.timedelta(seconds=int(seconds)))
    
    @property
    def precursor(self) -> Precursor:
        if self._precursor is None:
            raise PrecursorError(PrecursorError.PRECURSOR_PROPERTY)
        return self._precursor
    
    @precursor.setter
    def precursor(self, precur: Precursor) -> None:
        if not isinstance(precur, Precursor):
            raise PrecursorError(PrecursorError.PRECURSOR_INSTANCE.format('precursor'))
        self._precursor = precur
    
    @precursor.deleter
    def precursor(self) -> None:
        raise PrecursorError(PrecursorError.PRECURSOR_DELETE)
    
    def render(self) -> str:

        # Make sure precursor is available.
        if self._precursor is None:
            raise PrecursorError(PrecursorError.WIDGET_RENDER.format(self.__name__))
        
        return self.format.format(self.normalize_time(self.precursor.secondselapsed))
    
    @property
    def length(self) -> Union[int, UnknownLength]:
        return self._length
    
    @property
    def thread(self) -> Thread:
        if self._precursor is None:
            raise PrecursorError(PrecursorError.PRECURSOR_THREAD)
        return self.precursor.threads[self.__name__]
    
    @property
    def is_sensitive(self) -> bool:
        return True

@override.cls
class ETA(Time, PrecursorFeature):
    __name__: str = 'ETA'

    @override.mtd
    def __init__(self, format: str = 'ETA: {}') -> None:
        self.format = format
        self._precursor: Precursor = None
        self._length = len(self.format.format('--:--:--'))
    
    @override.mtd
    def render(self) -> str:
        if self.precursor.totalwork == 0 or self.precursor.totalwork == float(0) or self.precursor.complete == 0 or self.precursor.complete == float(0):
            return self.format.format('--:--:--')
        elif self.precursor.totalwork == self.precursor.complete:
            return 'Time: {}'.format(self.normalize_time(self.precursor.secondselapsed))
        else:
            elapsed = self.precursor.secondselapsed
            eta = elapsed * self.precursor.totalwork / self.precursor.complete - elapsed
            return self.format.format(self.normalize_time(eta))

@override.cls
class AdaptiveETA(ETA, PrecursorFeature):
    __name__: str = 'AdaptiveETA'
    NUM_SAMPLES = 10

    def _update_samples(self, complete: Union[int, float], elapsed: float) -> Tuple[Union[int, float], float]:
        sample = (complete, elapsed)
        if not hasattr(self, 'samples'):
            self.samples = [sample] * (self.NUM_SAMPLES + 1)
        else:
            self.samples.append(sample)
        return self.samples.pop(0)

    def _eta(self, totalwork: Union[int, float], complete: Union[int, float], elapsed: float) -> float:
        return elapsed * totalwork / float(complete) - elapsed
    
    @override.mtd
    def render(self) -> str:
        if self.precursor.totalwork == 0 or self.precursor.totalwork == float(0) or self.precursor.complete == 0 or self.precursor.complete == float(0):
            return self.format.format('--:--:--')
        elif self.precursor.totalwork == self.precursor.complete:
            return 'Time: {}'.format(self.normalize_time(self.precursor.secondselapsed))
        else:
            elapsed = self.precursor.secondselapsed
            complete1, elapsed1 = self._update_samples(self.precursor.complete, elapsed)
            eta = self._eta(self.precursor.totalwork, self.precursor.complete, elapsed)
            if self.precursor.complete > complete1:
                etastamp = self._eta(self.precursor.totalwork - complete1,
                                     self.precursor.complete - complete1,
                                     elapsed - elapsed1)
                weight = (self.precursor.complete / float(self.precursor.totalwork)) ** 0.5
                eta = (1 - weight) * eta + weight * etastamp
            return self.format.format(self.normalize_time(eta))

class FileTransferSpeed(Widget, PrecursorFeature):
    ...

class Tint(WidgetWrapper):
    def __init__(self, widget: Union[WidgetType, CustomRenderType], **kwargs: str) -> None:
        self.kwargs = kwargs
        self.widget = widget

        if isinstance(self.widget, CustomRender):
            setattr(self, 'set_possible_length', self.widget.set_possible_length)
            setattr(self, 'set_normalization', self.widget.set_normalization)
       
        setattr(self, '__name__', self.widget.__name__)

        if hasattr(self.widget, '__precursor__'):
            if getattr(self.widget, '__precursor__') == 'enabled':
                # this should support the normal mechanism based on whatever widget is passed.
                setattr(self, '__precursor__', 'enabled')
            else:
                setattr(self, '__precursor__', 'disabled') # experimental, No functionality yet with 'disabled'.
    
    def render(self) -> str:
        rendered = ''
        if isinstance(self.widget, Label):
            if 'label' in self.kwargs:
                rendered += str(self.kwargs['label']) + self.widget.label + Color.RED.reset
            else:
                rendered += self.widget.label
            
            if 'separator' in self.kwargs:
                rendered += str(self.kwargs['separator']) + self.widget.separator + Color.RED.reset
            else:
                rendered += self.widget.separator

            return rendered
        elif isinstance(self.widget, Bar):
            # length_of_finished_marker = len(self.widget.finished_marker)
            # length_of_unfinished_marker = len(self.widget.unfinished_marker)
            pre_rendered = self.widget.render()
            length_of_start_marker = len(self.widget.start_marker)
            length_of_end_marker = len(self.widget.end_marker)
            length_of_finished_marker = self.widget.finished
            length_of_unfinished_marker = self.widget.unfinished
            
            if 'start_marker' in self.kwargs:
                rendered += str(self.kwargs['start_marker']) + pre_rendered[0:length_of_start_marker] + Color.RED.reset
            else:
                rendered += pre_rendered[0:length_of_start_marker]
            
            if 'finished_marker' in self.kwargs:
                rendered += str(self.kwargs['finished_marker']) + pre_rendered[length_of_start_marker:length_of_finished_marker + length_of_start_marker] + Color.RED.reset
            else:
                rendered += pre_rendered[length_of_start_marker:length_of_finished_marker + length_of_start_marker]
            
            if 'unfinished_marker' in self.kwargs:
                rendered += str(self.kwargs['unfinished_marker']) + pre_rendered[length_of_finished_marker + length_of_start_marker:length_of_unfinished_marker + length_of_finished_marker + length_of_start_marker] + Color.RED.reset
            else:
                rendered += pre_rendered[length_of_finished_marker + length_of_start_marker:length_of_unfinished_marker + length_of_finished_marker + length_of_start_marker]
            
            if 'end_marker' in self.kwargs:
                rendered += str(self.kwargs['end_marker']) + pre_rendered[length_of_unfinished_marker + length_of_finished_marker + length_of_start_marker:length_of_end_marker + length_of_unfinished_marker + length_of_finished_marker + length_of_start_marker] + Color.RED.reset
            else:
                rendered += pre_rendered[length_of_unfinished_marker + length_of_finished_marker + length_of_start_marker:length_of_end_marker + length_of_unfinished_marker + length_of_finished_marker + length_of_start_marker]
            
            return rendered
        elif isinstance(self.widget, Time):
            if 'format' in self.kwargs:
                rendered += str(self.kwargs['format']) + self.render() + Color.RED.reset
            else:
                rendered += self.render()
            
            return rendered
        else:
            return rendered
    
    @property
    def length(self) -> Union[int, UnknownLength]:
        return self.widget.length

    @property
    def is_sensitive(self) -> bool:
        return self.widget.is_sensitive
    
    @property
    def precursor(self) -> Precursor:
        return self.widget.precursor
    
    @precursor.setter
    def precursor(self, precur: Precursor) -> None:
        self.widget.precursor = precur
    
    @precursor.deleter
    def precursor(self) -> None:
        raise PrecursorError(PrecursorError.PRECURSOR_DELETE)

    @property
    def thread(self) -> Thread:
        return self.widget.thread