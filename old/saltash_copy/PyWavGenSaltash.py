'''

PyWavGenSaltash 1.0, A Python Wave Generator

Saltash, A Python based wave generator and synthesis specification



The main object is "WaveForm", different types of waves inherit from this.


render_wave(SineWave(frequency=cycles), 'SineWave.wav')



key properties of waves:

frequency
amplitude
full_range ... True if full range wave from -1 to 1 (as opposed to 0 to 1) ... all generators are half range (even sine waves are made 0-1)
invert ... wave is flipped upside down
phase
saturate ... is like a compression on a wave that acts in full range (squidges a sine symmetrically), needs to be applied to full range signal atm
pulse_width ... changes the pulse width of a sqaure, affects some other waves to in similar sounding ways (pinched saw, triangle)
exp ... like saturate but one sided, as if saturating a signal in a one sided manner (one a saw this makes bowed volume curves)



working notes:
currently exp is applied to the signal when it is half range
saturate is applied after (and if) it is converted to full range (it is the same as exp if half range)

the two functions might be consolidated, and signal flow regarding the add_waves and ring mod etc might be a bit unclear



'''
from __future__ import absolute_import, division, print_function
# import numpy as np
# import matplotlib.pyplot as plt
import wave as PythonWave  # avoid importing wave to top level to avoid potential conflicts with "wave"
import struct
import random
import math
import copy
import os
from distutils.dir_util import mkpath  # Saltash functions automaticly create directories if required


# print('loading saltash (python wave generator) v1.0...')
sample_rate = 48000
# print('sample_rate:', sample_rate)
Afreq = 440
# print('Afreq:', Afreq)
Cfreq = Afreq * 2 ** (-9 / 12)  # middle C
# print('Cfreq:', Cfreq)

render_log = []  # saves a list of rendered files


def pitch_to_frequency(note=0):
    '''
    convert a note to a frequency
    note = 0 gives a middle C (261Hz)
    note = 9 gives the A (440Hz)
    '''
    return 440 * 2 ** ((note - 9) / 12)


def normalize_array(array):
    '''
    finds the min and max values of an array of values, scales all the values to ensure they range from 0-1
    for example, it would scale a full range sine wave to only be positive

    NOTE, need to add full range normalisation

    '''
    ret = []
    max_val = 0
    min_val = 0
    for val in array:  # find max and min value
        if val > max_val:
            max_val = val
        if val < min_val:
            min_val = val
    val_range = max_val - min_val  # find range
    for val in array:  # build normalized array
        val = val - min_val
        if val_range != 0:
            val /= val_range

        ret.append(val)
    return ret


def array_to_wav_file(array, filename='function_waveform_gen_test.wav', sample_rate=48000, normalize=True, full_range=False):
    '''
    save an array of values to a wav file at a given sample rate
    array should be from 0 to 1
    array is automaticly normalized ensuring all values are from zero to one (if normalize is true)


    code has now been modified to accept full-range input, it used to accept 0-1, now it accepts -1to1

    '''
    if normalize:
        array = normalize_array(array)  # automaticly normalise (prevent crash)

    mkpath(os.path.dirname(filename))
    wave_output = PythonWave.open(filename, 'w')
    # (nchannels, sampwidth, framerate, nframes, comptype, compname)
    # sampwidth is the amount of bytes per a sample, normal would be 2 for 16 bit
    wave_output.setparams((1, 2, sample_rate, 0, 'NONE', 'not compressed'))
    values = []

    # for n in range(0, len(array)): #THIS CODE MUST HAVE BEEN FROM SOME SINE GENERATION OR SOMETHING (preserving n)
    #     # Value = int((array[n] - .5) * 2 * 32767) #ORGINAL CODE, tying HACKS, this code seems to convert a float 0-1 to a int (-32767 to 32767)
    #     Value = int(array[n] * 32767) #try to modify to a direct int conversion (accept full range signals)
    #     Packed_Value = struct.pack('h', Value)
    #     Values.append(Packed_Value)

    for value in array:
        if not full_range:  # if signal is already full range we skip this bit
            value = (value - 0.5) * 2  # only fun this bit if coming from a half range signal (0 to 1)
        value = int(value * 32767)  # try to modify to a direct int conversion (accept full range signals)
        packed_value = struct.pack('h', value)
        values.append(packed_value)

    # we convert our values to a string to allow writing to the wav object (weird but works, performance unknown)
    value_str = ''.join(values)
    wave_output.writeframes(value_str)

    render_log.append(filename)  # stores a list of rendered waves during session for debug


class WaveForm:
    '''
    the main object of this program, represets a wavefunction with many applicable features
    does not generate the actual samples until requested

    the waveform does not have any idea of samplerates etc, so it just represents, typically, one cycle of a wave (at frequency 1)

    many features are by default set to "None", this means the feature is turned off
    '''

    saturate = 1  # testing sturation

    frequency = 1
    sync = False  # if this wave is called by parent wave, multiply the frequency
    amplitude = 1  # signal multiplied by this
    offset = 0
    phase = 0
    # causes the signal to be inverted (note this relies on the "invert profile" as full range signals need to invert differently)
    invert = False
    # 0 is for positive waves (square,saw), 1 for full range (sine)... waves will not invert properly if profile is wrong
    invert_profile = 0

    generator_is_full_range = False  # perhaps replacing the "invert profile" UNUSED ATM

    # TODO, will turn a signal that is not normally full range, like saw to a full range signal
    full_range = False

    # pulse width affects certain waves like square (default 0.5), some other waves have an emulation of pulse width
    pulse_width = 0.5
    mod = 0
    exponent = 1

    # used to clip the signal, for example set max 0.7 and min -0.7 on a sine wave to hard clip the wav (if left to None does not apply)
    # maximum signal level (limiter)
    maximum = None
    # minimum signal level (limiter)
    minimum = None

    # frequency mod wave, multiplies frequency
    frequency_mod = None
    # amplitude mod wave (or list of waves), multiplies amplitude (like a ring mod)
    amplitude_mod = None
    phase_mod = None
    pulse_width_mod = None
    mod1_mod = None
    mod2_mod = None
    exp_mod = None

    sync_wave = None

    # add this wave (or list of waves) to amplitude at very end of chain
    add_wave = None

    steps = None  # if a number, makes this the number of steps accross a wave, like 16 is a 16 step sine wave

    square_sequence = None

    def __init__(self, **kwargs):
        self.add_wave = []  # default val

        for key in kwargs:
            try:
                # causes an AttributeError if unregistered parameter
                getattr(self, key)
            except AttributeError as e:  # the par does not exist!
                print(type(e), e, '(you may have entered an unregistered parameter!)')
                raise

            val = kwargs[key]
            setattr(self, key, val)
        pass

    def __add__(self, other):  # return a new wave like a chord
        wave1 = copy.deepcopy(self)
        wave2 = copy.deepcopy(other)
        new_wave = WaveForm()  # this wave is a comtainer for these waves
        new_wave.add_wave = [wave1, wave2]
        new_wave.function = None
        return new_wave

    # def function(self, x):
    #     '''
    #     the actual generator function of the wave
    #     '''
    #     return 1
    # the main function called by the wave, if none, a default 0 signal is returned
    function = None

    def get_pos(self, x, sync_frequency=1):
        '''
        gets the signal (y) at any given position (x)
        it calls the function but also has to take into account all the settings like amplitude, frequency etc
        also modulations TODO

        sync_frequency multiplies the wave frequency, used called when waves have "sync" activated

        the weakness of this design is it will not be able to apply an effect that has knowledge of the previous signal levels
        an example would be a low pass filter, that generally needs to know about the previous signal level
        '''

        frequency = self.frequency
        frequency *= sync_frequency  # apply a multiplier to wave for sync

        if self.steps is not None:
            x *= (self.steps * frequency)
            x = int(x)
            x /= (self.steps * frequency)
            pass

        amplitude = self.amplitude

        phase = self.phase

        if self.phase_mod is not None:  # ADD LIST SUPPORT
            if self.phase_mod.sync:  # SYNC UNTESTED
                phase = self.phase_mod.get_pos(x, frequency)
            else:
                phase = self.phase_mod.get_pos(x)

        if self.pulse_width_mod is not None:  # ADD LIST SUPPORT
            if self.pulse_width_mod.sync:  # SYNC UNTESTED
                self.pulse_width = self.pulse_width_mod.get_pos(x, frequency)
            else:
                self.pulse_width = self.pulse_width_mod.get_pos(x)

        if self.frequency_mod is not None:  # if we have a frequency modulation wave, apply this to our frequency #ADD LIST SUPPORT
            if self.frequency_mod.sync:
                # SYNC UNTESTED, possible bug with where this frequency is multiplied
                # frequency *= self.frequency_mod.get_pos(x, frequency) #SHUTDOWN FOR DEBUG
                pass
            else:
                frequency *= self.frequency_mod.get_pos(x)

        offset = 0  # we build the final offset here as we want to invert the signal before applying any user offset

        invert_profile = self.invert_profile
        if self.full_range is not None:  # a bit of a hack concerning inverting
            if self.full_range:
                invert_profile = 1

        # the way to invert the signal can depend on if it is a half or full range signal (like a saw vs sine)
        if self.invert:
            if invert_profile == 0:  # for half range like saw
                amplitude = -amplitude  # the values now go negative
                offset = self.amplitude  # so offset the wave
            elif invert_profile == 1:  # full range signals invert easier
                amplitude = -amplitude  # simply flip the amplitude

        offset += self.offset  # add the user offset
        # frequency applied to position, then phase offset applied (0.5 is out of phase)
        val = 0

        if self.function is not None:
            val = self.function(x * frequency + phase)

        val = val ** self.exponent  # before full range mean we can use fractional powers

        if self.full_range:
            val *= 2
            val -= 1

        if self.saturate is not None:
            '''
            trying to make a volume curve, such that boosts low signals more than high ones
            '''

            # # saturate_test works but only does one ratio atm, can't figure where to put number
            # sat_repeats = self.saturate2
            # for i in range(sat_repeats):
            #     saturate = self.saturate
            #     saturate_offset = abs(val)  # offset is a 0-1
            #     saturate_offset *= saturate
            #     saturate_offset = saturate - saturate_offset  # should be number that tends towards 1 when it signal drops to 0, 0 when signal is 1
            #     sat_multiply = 1 + saturate_offset
            #     val *= sat_multiply

            #
            # saturate = self.saturate
            # saturate2 = self.saturate2
            # saturate = 1
            # saturate2 = 5
            # saturate_offset = abs(val)  # offset is a 0-1
            # saturate_offset *= saturate
            # saturate_offset = (saturate - saturate_offset) * saturate2  # should be number that tends towards 1 when it signal drops to 0, 0 when signal is 1
            # sat_multiply = 1 + saturate_offset
            # val *= sat_multiply

            # for i in range(2): #first working version, required repeats of same algo
            #     saturate = self.saturate
            #     saturate = 1  # 1 works, 2 weird sat
            #     saturate_offset = abs(val)  # offset is a 0-1
            #     saturate_offset = (1 - saturate_offset) * saturate  # should be number that tends towards 1 when it signal drops to 0, 0 when signal is 1
            #     sat_multiply = 1 + saturate_offset
            #     val *= sat_multiply

            # final saturate method! remove negative, apply exponenent, then restore the negative sign if required
            # for normal results, apply on full range sine curve, pushes the sine towards a square
            # on a half range saw, is the same as an "exp" wave

            # will remove the negative, apply exponenent, and then return the negative
            pos_val = abs(val)
            val_is_neg = val < 0
            pos_val = pos_val ** (1 / self.saturate)
            val = pos_val
            if val_is_neg:
                val = -val

        val *= amplitude
        val += offset

        # if we have one or more addwaves, these are added to the signal (used for chords)
        if self.add_wave is not None:
            add_wave = self.add_wave
            add_wave_type = type(add_wave)
            if add_wave_type is not list:
                add_wave = [add_wave]
            for add_wave1 in add_wave:
                if add_wave1.sync:
                    val += add_wave1.get_pos(x, sync_frequency=frequency)
                else:
                    val += add_wave1.get_pos(x)

        if self.amplitude_mod is not None:  # multiplies volume, can be used for gating or ring modulation
            ''' OLD CODE
            # if self.amplitude_mod.sync:  # sync mode, multiplies waves
            #     val *= self.amplitude_mod.get_pos(x, frequency)
            # else:
            #     val *= self.amplitude_mod.get_pos(x)
            '''
            # code to accept a list of amplitude mods
            amplitude_mod = self.amplitude_mod
            amplitude_mod_type = type(amplitude_mod)
            if amplitude_mod_type is not list:
                amplitude_mod = [amplitude_mod]
            for mod in amplitude_mod:
                if mod.sync:
                    val *= mod.get_pos(x, frequency)  # use a sync frequency
                else:
                    val *= mod.get_pos(x)

        # if self.square_sequence is not None: #NEW WORKING CODE, APPLY SQUARE SEQ AS DEFAULT
        #     '''
        #     x %= 1
        # x *= len(self.square_sequence)
        # x = int(x)
        # return self.square_sequence[x]
        #     '''
        #     sq_x = x % 1
        #     sq_x *= len(self.square_sequence)
        #     sq_x = int(sq_x)
        #     val *= self.square_sequence[sq_x]

        #     val *= 1

        if self.maximum is not None:  # clipping is applyed lastly to the signal, if applicable
            if val > self.maximum:
                val = self.maximum
        if self.minimum is not None:
            if val < self.minimum:
                val = self.minimum

        return val

    def get_samples(self, length, frequency=1):
        '''
        turn wave into samples, length determines the amount of samples (the resolution)
        '''
        samples = []
        for i in xrange(length):
            samples.append(self.get_pos(i / length, sync_frequency=frequency))
            # switched to a yield
            # yield self.get_pos(i / length, sync_frequency=frequency)
        return samples

    def plot(self, length=128, frequency=1, cycles=1):  # shortcut to plot this wave
        '''
        now with labels:
        https://matplotlib.org/users/legend_guide.html
        '''
        handles = []
        main, = plt.plot(list(self.get_samples(
            length=length, frequency=frequency)), label='main')
        handles.append(main)

        plt.legend(handles=handles)
        plt.show()

        '''
        line_up, = plt.plot([1,2,3], label='Line 2')
        line_down, = plt.plot([3,2,1], label='Line 1')
        plt.legend(handles=[line_up, line_down])
        '''

    def preview(self, cycles=8):
        '''
        render temp file and open in os
        '''
        filename = './temp_saltash/temp.wav'
        sample_rate = 48000
        self.render_to_wav(length = sample_rate/Cfreq*cycles, frequency=cycles, filename=filename)
        os.system('open '+ filename)



    def render_to_wav(self, length, filename, sample_rate=48000, frequency=1):
        '''
        render this wave to a wav file
        note that if the sample rate was 48kHz
        48000 samples would be one second
        A middle C is 261.62Hz
        If this wave therefore had a frequency of 1, then to make a C with one occilation
        we would need 48000/261.62Hz samples
        this would make one cycle of a middle C at 48kHz
        '''
        # round the length, incase it was a fraction
        print('rendering \"{}\"'.format(filename))

        length = int(round(length))
        array_to_wav_file(array=self.get_samples(length=length, frequency=frequency),
                          filename=filename, sample_rate=sample_rate)


class SineWave(WaveForm):
    '''
    standard sine wav
    '''
    # invert_profile = 1  # this marker tells us it is a full range signal (used in case we want to invert it)
    generator_is_full_range = True

    def function(self, x):
        # return math.sin(math.radians(x * 360))
        # generating a positive sine and correcting it
        return math.sin(math.radians(x * 360)) / 2 + 0.5


class PositiveSineWave(WaveForm):
    '''
    positive only sinewave (ranges from 0 to 1)
    '''

    def function(self, x):
        return math.sin(math.radians(x * 360)) * 0.5 + 0.5


class SquareWave(WaveForm):
    '''
    standard square wav with a pulse width (normal square is 0.5)
    '''
    pulse_width = 0.5

    def function(self, x):
        if x % 1 < self.pulse_width:
            return 1
        else:
            return 0


class SawWave(WaveForm):
    '''
    standard saw wave, rises over cycle
    '''

    def function(self, x):
        return x % 1


class TriangleWave(WaveForm):
    '''
    standard triangle wave with added pulse width (moves the peak of the triangle, meaning the wav becomes a saw)
    '''
    pulse_width = 0.5

    def function(self, x):
        wav_pos = x % 1
        if wav_pos < self.pulse_width:
            wav_pos = wav_pos / self.pulse_width
            return wav_pos
        else:
            wav_pos -= self.pulse_width
            wav_pos = wav_pos / (1 - self.pulse_width)
            return 1 - wav_pos


class PinchedSawWave(WaveForm):
    '''
    saw wave wih pulse width, basicly two saws one after the other and making one smaller than the other
    '''
    pulse_width = 0.5

    def function(self, x):
        # x /= 2  # correct frequency
        wav_pos = x % 1
        if wav_pos < self.pulse_width:
            wav_pos = wav_pos / self.pulse_width
            return wav_pos
        else:
            wav_pos -= self.pulse_width
            wav_pos = wav_pos / (1 - self.pulse_width)
            return wav_pos


class ExpSawWave(WaveForm):
    '''
    DEPRECIATED AS WE HAVE ADD AND "exp" property

    a saw wave that rises expotentially, when exp is > 1 (like 2 for example), it looks like bowed saw tooths
    exp at 1 would make a regular saw
    exp < 1 makes an opposite bow

    the properties of this wave are useful for envelopes
    '''
    exp = 2

    def function(self, x):
        x = x % 1
        return x ** self.exp
        pass


class NoiseWave(WaveForm):
    '''
    procedural noise generator
    '''
    seed = 0

    def function(self, x):
        random.seed(x % 1 + self.seed)
        return random.random()


class RandomSquareWave(NoiseWave):
    steps = 16


class ClippedSineWave(SineWave):
    '''
    example of clipping a sine wave
    '''
    amplitude = 1.1
    maximum = 1
    minimum = -1

# class RandomSquareWave(WaveForm): #base on an aliased wav
#     pass


class SteppedSineWave(SineWave):
    steps = 16


class SquareSequenceWave(WaveForm):
    '''
    wave built of a custom array sequence
    '''
    square_sequence = [1, 0, 1, 1, 0, 1, 1, 1]

    def function(self, x):
        x %= 1
        x *= len(self.square_sequence)
        x = int(x)
        return self.square_sequence[x]


class GatedSquareWave(SquareWave):
    '''
    demo of how to gate a square signal
    '''
    frequency = 16  # 8 allows the gate to fully display one cycle
    amplitude_mod = SquareSequenceWave(
        frequency=1 / frequency, sync=True, square_sequence=[1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1])


def plt_add_wave(wave, cycles=1, samples=128):
    '''
    quick shortcut to plotting my waves for testing
    '''
    plt.plot(wave.get_samples(samples) * cycles)
    plt.legend(['wav1', 'wav2', 'wav3', 'wav4',
                'wav5', 'wav6', 'wav7', 'wav8'])


# plt_add_wave(SineWave(frequency=3))
# plt_add_wave(SineWave(frequency=3, phase=0.5))
# # plt_add_wave(SineWave(invert = True))
# # plt_add_wave(PositiveSineWav())
# plt_add_wave(SquareWave(frequency=4))
# plt_add_wave(SquareWave(frequency =4,phase=0.5))
# plt_add_wave(SquareWave(frequency=4, phase=0.25))
# # plt_add_wave(SquareWave(invert=True))
# # plt_add_wave(SawWave())
# # plt_add_wave(SawWave(invert = True, amplitude = 2, frequency = 3))
# # plt_add_wave(SawWave(frequency = 8))
# # plt_add_wave(TriangleWave())
# # plt_add_wave(PinchedSawWave())
# # plt_add_wave(SquaredDropWave())
# plt_add_wave(SquareWave(frequency=2, phase=0, amplitude=2, offset=0, invert=False))
# plt_add_wave(SquareWave(frequency=2, phase=0, amplitude=2, offset=-1, invert=True))
# # plt_add_wave(NoiseWave())


# squarewave = PositiveSineWav(amplitude=1, offset=0, invert=False)
# plt_add_wave(squarewave)
# squarewave.render_to_wav(48000, 'ob_render_square_test.wav')

# squarewave1 = PositiveSineWav(amplitude=1, offset=0, invert=True)
# plt_add_wave(squarewave1)
# squarewave1.render_to_wav(48000, 'ob_render_square1_test.wav')

# plt_add_wave(SawWave(frequency=16, amplitude_mod=PositiveSineWave())) #ring mod example


# plt_add_wave(SineWave(frequency=2, amplitude = 0.5, offset = 0.5, invert = True))
# plt_add_wave(SineWave(frequency=2, amplitude = 0.25, offset = 0.5, invert = True, phase = 0))
# plt_add_wave(SineWave(frequency=2, amplitude = 0.25, offset = 0.5, invert = True, phase = 0.5))


def gen_c_example_waves():

    # use our tool to make a load of C waves as examples
    cycles = 1
    cycles = 64
    # cycles = 1
    length = sample_rate / Cfreq * cycles * 1

    def render_wave(wave, filename):
        wave.render_to_wav(length=length, filename=filename)
        # plt_add_wave(wave)

    render_wave(SineWave(frequency=cycles), 'sine.wav')
    render_wave(SquareWave(frequency=cycles), 'square.wav')
    render_wave(SquareWave(frequency=cycles,
                           pulse_width=0.2), 'square_pw02.wav')
    render_wave(SawWave(frequency=cycles), 'saw.wav')
    render_wave(TriangleWave(frequency=cycles,
                             pulse_width=0.5), 'triangle.wav')
    render_wave(PinchedSawWave(frequency=cycles / 2,
                               pulse_width=0.2), 'pinched_saw_pw02.wav')
    render_wave(ExpSawWave(frequency=cycles), 'exp_saw.wav')
    render_wave(NoiseWave(frequency=cycles), 'noise.wav')
    render_wave(ClippedSineWave(frequency=cycles), 'clipped_sine.wav')

    render_wave(SineWave(frequency=cycles, amplitude_mod=TriangleWave(
        frequency=1 / 16)), 'amp_mod.wav')

    ring_mod_saw_8 = SawWave(
        frequency=cycles, amplitude_mod=PositiveSineWave(frequency=cycles / 8))
    render_wave(ring_mod_saw_8, 'ring_mod_saw_8.wav')
    ring_mod_square_8 = SquareWave(
        frequency=cycles, amplitude_mod=PositiveSineWave(frequency=cycles / 8))
    render_wave(ring_mod_square_8, 'ring_mod_square_8.wav')


# gen_c_example_waves()

def gen_test_waves():
    cycles = 256
    length = sample_rate / Cfreq * cycles * 1

    def render_wave(wave, filename):
        wave.render_to_wav(length=length, filename=filename)

    pwm_mod = SawWave(invert=True)
    # pwm_mod = ExpSawWave(invert = True)
    render_wave(SquareWave(frequency=cycles, pulse_width_mod=pwm_mod),
                filename='test_square_pwm256.wav')

    render_wave(SineWave(frequency=cycles, steps=8),
                filename='test_step_sin.wav')
    render_wave(SineWave(frequency=cycles, steps=16),
                filename='test_step_sin2.wav')
    render_wave(NoiseWave(frequency=cycles, steps=16),
                filename='test_ran_square.wav')

    render_wave(SineWave(frequency=cycles, frequency_mod=SawWave(
        amplitude=0.5, invert=True)), filename='test_pitch_drop.wav')

    pass
# gen_test_waves()


# plt.show()


# fq frequency


# vol amplitude
# fr full_range
# iv invert
# ph phase
# sat saturate
# pw pulse_width
# exp exp

# fqM


saltash_par_info_key = ['name', 'abbreviation', 'default value', 'details']
saltash_par_info = [
    ['frequency', 'fq', WaveForm.frequency, 'total oscillations to be rendered'],
    ['amplitude', 'vol', WaveForm.amplitude, 'peak amplitude of wave'],
    ['full_range', 'fr', WaveForm.full_range, 'if True wave is -1 to 1, if False it is 0 to 1'],
    ['invert', 'iv', WaveForm.invert, 'flip the wave upside down'],
    ['phase', 'ph', WaveForm.phase, 'phase'],
    ['pulse_width', 'w', WaveForm.pulse_width, 'pulse width of square of other functions for other waves'],
    ['saturate', 'sat', WaveForm.saturate, 'like an axp that works on full-range signals, flattens full range sine to square for example'],
    ['exponent', 'exp', WaveForm.exponent, 'like saturate but just applied on positive signal, can make an exp saw (a bowed saw)'],
]


if __name__ == "__main__":
    print('running tests...')
    cycles = 2
    filename = 'out/test.wav'
    test = SineWave(amplitude=1, frequency=cycles, exponent=1, full_range=True, saturate=2)
    test.render_to_wav(Cfreq * cycles, filename)
    os.system('open ./' + filename)

    for entry in saltash_par_info:
        print(entry)
