'''

A GUI Grid using Tkinter


'''
from __future__ import absolute_import, division, print_function
import PyWavGenSaltash
# from Tkinter import *

import Tkinter as tk

import os
import json
from collections import OrderedDict
from distutils.dir_util import mkpath


import hashlib


def md5(filename):
    hash_md5 = hashlib.md5()
    byte_count = 0
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
            byte_count += len(chunk)
    # print('md5 chunk_count', byte_count, byte_count/1024)
    return hash_md5.hexdigest()


def md5_and_size(filename):
    hash_md5 = hashlib.md5()
    byte_count = 0
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
            byte_count += len(chunk)
    # print('md5 chunk_count', byte_count, byte_count/1024)
    return hash_md5.hexdigest(), byte_count


class MyGrid():  # an editable grid that saves

    keys = ['Entry', 'Checkbutton', 'list', 'None', 'Eval']
    labels = [None] * 5
    columns = len(keys)
    key_types = ['Entry', 'Checkbutton', ['hello', 'option'], None, 'Eval']
    default_values = [None] * 5

    # keys = []
    # columns = 0
    # key_types = []
    # default_values = []

    '''
    key types:
    None
    Checkbutton
    ['option1', 'option2']


    '''

    # validate_functions = [None]

    # key_types = None  # if none, assume all are "entry"

    rows = 8

    column = 0
    row = 0
    command_row = 0

    data = None

    show_header = True

    json_filename = 'AbstractGUI.json'

    load_json = True

    autosave = True  # automaticly save everytime _set_data is called

    show_column_labels = True  # use laels if possible, keys if no label


    # def width(self):
    #     return len(self.keys)

    def update_column_widths(self):
        '''
        adjusts the widths of all the widgets according to self.column_widths
        can only be called after __init_gui__ (widgets need to exist)
        '''
        print(self.column_widths)
        for x in range(len(self.column_widths)):
            width = self.column_widths[x]

            self.header_widgets[x].config(width=width)  # also header

            for y in range(len(self.widgets)):
                widget = self.widgets[y][x]
                if widget is not None:
                    widget.config(width=width)

    def delete_columns(self):
        '''
        blanks all the columns
        can only be called prior to __init_gui__
        '''
        self.keys = []  # the column key
        self.labels = []  # optional label, if None, use key
        self.column_widths = []  # widget widths
        self.key_types = []  # types, like Entry, OptionMenu etc
        self.default_values = []  # default of column cells
        self.functions = []  # called on button press
        self.columns = 0  # set column count to 0

    def add_column(self, key='col1', key_type='Entry', default_value=None, width=0, label=None, function=None):
        '''
        can only be called prior to __init_gui__, used to make setting columns easier
        '''

        # self.columns += 1
        # if self.keys is None:
        #     self.keys = []
        # if self.key_types is None:
        #     self.key_types = []
        # if self.default_values is None:
        #     self.default_values = []

        # if self.data is None: #expand data?
        #     self.data = []
        #     for i in range(self.rows):
        #         self.data.append([])
        # for row in self.data:
        #     row.append(default_value)

        if type(key_type) == list:  # if list but no default value, use first item
            if default_value is None and len(key_type) > 0:
                default_value = key_type[0]
        elif key_type == 'Entry' and default_value is None:
            default_value = ''
            pass
        elif key_type == 'Checkbutton' and default_value is None:
            default_value = 0
            pass

        self.keys.append(key)
        self.key_types.append(key_type)
        self.default_values.append(default_value)
        self.column_widths.append(width)
        self.labels.append(label)
        self.functions.append(function)
        self.columns += 1

    def reset_grid_data(self):
        '''
        set all data to default values
        '''
        self.data = []
        for y in range(self.rows):
            row = []
            for x in range(self.columns):
                if self.default_values is not None:
                    row.append(self.default_values[x])
                else:
                    row.append('')
            self.data.append(row)

    def save(self):
        '''
        save the data to a json file
        '''
        print('saving data to \"{}\"'.format(self.json_filename))
        save_data = {}
        save_data['data'] = self.data
        save_data['keys'] = self.keys
        save_data['key_types'] = self.key_types
        save_data['default_values'] = self.default_values
        mkpath(os.path.dirname(self.json_filename))
        with open(self.json_filename, 'w') as f:
            f.write(json.dumps(save_data))

    def load(self):
        '''
        load data from json file
        '''
        if not os.path.isfile(self.json_filename):
            self.reset_grid_data()
            self.save()
        with open(self.json_filename) as f:
            save_data = json.loads(f.read())
            self.data = save_data['data']

    _key_to_column_cache = None

    def key_to_column(self, s):
        '''
        get the column number from the name
        '''
        '''
        for i in range(len(self.keys)):
            if s == self.keys[i]:
                return i
        raise(Exception('INVALID KEY! \"{}\"'.format(s)))
        '''
        # cache method WARNING, do not change keys!
        if self._key_to_column_cache is None:
            self._key_to_column_cache = {}
            for i in range(len(self.keys)):
                self._key_to_column_cache[self.keys[i]] = i
        return self._key_to_column_cache[s]

        return 0

    def _get_data(self, row, column):
        if type(column) == str:
            column = self.key_to_column(column)

        return self.data[row][column]

    def _set_data(self, row, column, data):
        '''
        called by the widget events to set the internal data store (MAY CHANGE TO USE THE REF VARS LATER)
        '''
        if type(column) == str:
            column = self.key_to_column(column)

        key = self.keys[column]
        print('SET: {0}{1} ({2},{1}) = {3}'.format(key, row, column, data))
        self.data[row][column] = data

        if self.autosave:
            self.save()

    def init(self):
        print('INIT HOOK', self)

        pass

    def __init__(self, root, **kwargs):

        # self.keys = []
        # self.

        for key in kwargs:
            try:
                # causes an AttributeError if unregistered parameter
                getattr(self, key)
            except AttributeError as e:  # the par does not exist!
                print(type(e), e, '(you may have entered an unregistered parameter!)')
                raise

            val = kwargs[key]
            setattr(self, key, val)

        self.init()

        # self. __init_gui__(root)

    def menu_command(self):

        print('called menu command!!!', self)
        for entry_box in self.entry_boxes:
            print(entry_box)

    menu_dict = None

    def __init__menubar__(self, root):

        menubar = tk.Menu(root)

        menu_dict = self.menu_dict  # if we have a menu dict
        if menu_dict is not None:
            for cascade_name in menu_dict:
                val = menu_dict[cascade_name]
                menu = tk.Menu(menubar, tearoff=0)
                for option_name in val:
                    menu.add_command(label=option_name, command=val[option_name])
                menubar.add_cascade(label=cascade_name, menu=menu)

        ''' HARDCODED ONE
        if True:  # file menu
            filemenu = Menu(menubar, tearoff=0)
            filemenu.add_command(label="Open", command=self.menu_command)
            filemenu.add_command(label="Save", command=self.save)
            filemenu.add_separator()
            filemenu.add_command(label="menu_command", command=self.menu_command)
            filemenu.add_separator()
            filemenu.add_command(label="Exit", command=root.quit)

            menubar.add_cascade(label="File", menu=filemenu)
        if True:  # synth menu
            filemenu = Menu(menubar, tearoff=0)
            filemenu.add_command(label="menu_command", command=self.menu_command)

            menubar.add_cascade(label="Synth", menu=filemenu)
        '''

        '''
        menu_dict = OrderedDict()
        menu_dict['test1'] = self.menu_command
        menu_dict['test2'] = self.menu_command
        cust_menu = Menu(menubar, tearoff=0)
        for key in menu_dict:
            val = menu_dict[key]
            cust_menu.add_command(label=key, command=val)
        menubar.add_cascade(label="cust_menu", menu=cust_menu)
        '''
        ''' MENU EXAMPLE
        def hello():
            print ("hello!")

        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=hello)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_separator()
        filemenu.add_command(label="menu_command", command=self.menu_command)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)

        menubar.add_cascade(label="File", menu=filemenu)

        # # create more pulldown menus
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Cut", command=hello)
        editmenu.add_command(label="Copy", command=hello)
        editmenu.add_command(label="Paste", command=hello)
        menubar.add_cascade(label="Edit", menu=editmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=hello)
        menubar.add_cascade(label="Help", menu=helpmenu)
        '''

        # display the menu
        root.config(menu=menubar)


    def __init_gui__(self, root):

        self.entry_boxes = []

        self.widgets = []  # save a link to the widgets
        for y in range(self.rows + 1):  # create the nested lists (extra row for header)
            row = []
            for x in range(self.columns):
                row.append(None)
            self.widgets.append(row)

        self.__init__menubar__(root)

        if self.load_json:
            self.load()
        else:
            self.reset_grid_data()

        self.column = 0
        self.row = 0

        self.header_widgets = []
        if self.show_header:  # show a header label
            for i in range(len(self.keys)):
                key = self.keys[i]

                if self.show_column_labels:
                    label = self.labels[i]
                    if label is not None:  # if labels not none, use instead of key
                        key = label

                w = tk.Label(root, text=key)
                w.grid(row=self.row, column=self.column)
                self.widgets[self.row][self.column] = w
                self.header_widgets.append(w)
                self.column += 1
            self.row += 1
            self.column = 0

        self.row_data = []

        for y in range(self.rows):

            # d = [] #UNKNOWN
            # self.row_data.append(d)

            # for key in self.keys:
            for x in range(len(self.keys)):
                key = self.keys[x]

                def add_row():  # for some reason just adding function here makes difference!!! (KILLS REFERENCES??)

                    # var = StringVar(root)
                    # var.set('ggg')  # default first entry

                    row = self.command_row
                    column = self.column

                    widget = None  # if a widget is created, use this to save the reference

                    key_type = 'Entry'  # if no type specifications, assume Entry
                    if self.key_types is not None:
                        key_type = self.key_types[x]
                        # if key_type is None:
                        #     key_type = 'Entry'

                    # key_type = self.key_types[i]

                    if key_type is None:
                        pass
                    elif key_type == 'Entry':

                        var = tk.StringVar()
                        # entry = Entry(root, textvariable=v, width=10)
                        widget = tk.Entry(root, textvariable=var, width=10)
                        # entry.bg = 'green'
                        widget.config(bg='lightgreen')

                        self.entry_boxes.append(widget)

                        # entry.update()
                        var.set("a default value")

                        def callback(*args):  # varible change callback
                            print ("variable changed!")

                        # entry.setvar

                        var.set(self._get_data(row, column))  # load the varible from the python

                        var.trace("w", callback)

                        # d.append(entry)

                        # print(row)
                        widget.grid(row=self.row, column=self.column)

                        def event(event):
                            data = widget.get()
                            self._set_data(row, column, data)
                            # var.set(self._get_data(row, column))  # set again incase of validation change

                        # entry.bind("<Return>", lambda event: print('EVENT:', 'entry_name:', row, str(column), entry.get()))
                        widget.bind("<Return>", event)
                        widget.bind("<Tab>", event)

                    elif key_type == 'Eval':
                        var = StringVar()
                        # entry = Entry(root, textvariable=v, width=10)
                        widget = Entry(root, textvariable=var, width=10)
                        var.set("a default value")

                        def callback(*args):  # varible change callback
                            print ("variable changed!")

                        var.set(self._get_data(row, column))  # load the varible from the python

                        var.trace("w", callback)

                        # d.append(entry)

                        # print(row)
                        widget.grid(row=self.row, column=self.column)

                        def event(event):  # try to evaluate data
                            data = widget.get()
                            try:
                                def get(column, row):  # allows a command in eval cells that gets other cell
                                    return self._get_data(column=column, row=row)
                                data = eval(data)
                            except Exception as e:
                                print(type(e), e)
                            var.set(data)
                            self._set_data(row, column, data)
                            # var.set(self._get_data(row, column))  # set again incase of validation change

                        # entry.bind("<Return>", lambda event: print('EVENT:', 'entry_name:', row, str(column), entry.get()))
                        widget.bind("<Return>", event)
                        widget.bind("<Tab>", event)

                    elif key_type == 'Checkbutton':

                        v = tk.IntVar()
                        data = self._get_data(row, column)
                        if data == '':
                            data = False
                        v.set(data)
                        widget = tk.Checkbutton(root, width=2, variable=v, command=lambda: self._set_data(row, column, v.get()))
                        widget.grid(row=self.row, column=self.column)

                    elif key_type == 'Button':
                        def callback():
                            print ("clicked button!", self.keys[column], row)
                            function = self.functions[column]
                            if function is not None:
                                function(row)

                        widget = tk.Button(master, text="OK", command=callback)
                        widget.grid(row=self.row, column=self.column)

                    elif key_type == 'OptionMenu':
                        options = ['bod', 'apples', 'toatos']
                        var = StringVar(root)
                        data = self._get_data(row, column)
                        if data == '':
                            data = options[0]
                        var.set(data)
                        widget = OptionMenu(root, var, *(options),
                                            # command=lambda event: print('shititi', var.get())
                                            command=lambda event: self._set_data(row, column, var.get())
                                            )
                        widget.grid(row=self.row, column=self.column)

                    elif type(key_type) == list:  # if type is a list, make an options menu
                        options = key_type
                        var = tk.StringVar(root)
                        data = self._get_data(row, column)
                        if data == '':
                            data = options[0]
                        var.set(data)

                        widget = tk.OptionMenu(root, var, *(options),
                                               # command=lambda event: print('shititi', var.get())
                                               command=lambda event: self._set_data(row, column, var.get())
                                               )
                        widget.grid(row=self.row, column=self.column)

                    # elif isinstance(key_type, EntryType):  # UNUSED!!

                    #     if key_type._type == 'OptionMenu':
                    #         options = key_type.options
                    #         var = StringVar(root)
                    #         data = self._get_data(row, column)
                    #         if data == '':
                    #             data = options[0]
                    #         var.set(data)
                    #         OptionMenu(root, var, *(options),
                    #                    # command=lambda event: print('shititi', var.get())
                    #                    command=lambda event: self._set_data(row, column, key_type.verify(var.get()))
                    #                    ).grid(row=self.row, column=self.column)
                    #     elif key_type._type == 'Entry':
                    #         v = StringVar()
                    #         # entry = Entry(root, textvariable=v, width=10)
                    #         entry = Entry(root, textvariable=v, width=10)
                    #         v.set("a default value")

                    #         entry.setvar

                    #         v.set(self._get_data(row, column))

                    #         d.append(entry)

                    #         # print(row)
                    #         entry.grid(row=self.row, column=self.column)

                    #         def event(event):
                    #             set_val = key_type.verify(entry.get())  # check validate
                    #             if set_val is not None:  # if not none
                    #                 self._set_data(row, column, set_val)
                    #             v.set(self._get_data(row, column))  # set again incase of validation change

                    #         # entry.bind("<Return>", lambda event: print('EVENT:', 'entry_name:', row, str(column), entry.get()))
                    #         entry.bind("<Return>", event)
                    #         entry.bind("<Tab>", event)

                    else:
                        raise(Exception('unrecognized keytype \"{}\"'.format(key_type)))

                    self.widgets[self.row][self.column] = widget  # save a ref to the widget

                    widget.config(width=self.column_widths[self.column])  # TRY ADJUST WIDTH NOW

                    self.column += 1
                    # self.row+=1
                add_row()

            self.row += 1
            self.command_row += 1
            self.column = 0

        pass

        # print(self.row_data)


wavetypes = OrderedDict()
wavetypes['sine'] = None
wavetypes['saw'] = None
wavetypes['square'] = None
wavetypes['triangle'] = None
wavetypes['lambda'] = None
wavetypes_keys = list(wavetypes.keys())
print(wavetypes_keys)

note_letters = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]  # chromatic letters


mod_types = ['amp', 'freq', 'pw']


class MySynthGrid1(MyGrid):
    '''
    very simple, just has one modulation
    '''

    show_header = True

    def menu_command(self):

        print('called menu command!!!', self)
        # for entry_box in self.entry_boxes:
        #     print(entry_box)
        #     entry_box.config(bg='blue')

        for widget_row in self.widgets:
            for widget in widget_row:
                if widget is not None:
                    print(type(widget))
                    # widget.config(bg='blue')
                    # widget.config(bg='#fecc14')
                    # widget.config(fg='blue')
                    # widget.config(width = 5)

        self.update_column_widths()

    def button_render_command(self, row):

        print('attempt to render row', row, '...')

        # row = self.data[row]
        # print(row)

        # try:
        #     pw = float(pw)
        # except Exception as e:
        #     print(type(e), e)
        #     pw = 0.5

        def get(key):
            data = self._get_data(row=row, column=key)
            try:
                data = float(data)
            except Exception as e:
                print(type(e), e)
            return data

        wave = get('wave')
        note = get('note')
        full_range = bool(get('full_range'))
        invert = bool(get('invert'))
        phase = get('phase')
        saturate = get('saturate')
        pulse_width = get('pulse_width')
        exp = get('exp')
        mod_type = get('mod_type')
        mod_wave = get('mod_wave')
        mod_period = get('mod_period')
        mod_full_range = bool(get('mod_full_range'))
        mod_invert = bool(get('mod_invert'))
        mod_phase = get('mod_phase')
        mod_amp = get('mod_amp')
        mod_exp = get('mod_exp')
        mod_offset = get('mod_offset')

        # note = self._get_data(row=row, column='note')
        # invert = bool(self._get_data(row=row, column='invert'))
        # mod_type = self._get_data(row=row, column='mod_type')
        # mod_wave = self._get_data(row=row, column='mod_wave')
        # mod_period = float(self._get_data(row=row, column='mod_period'))
        # mod_amp = float(self._get_data(row=row, column='mod_amp'))
        # mod_full_range = bool(self._get_data(row=row, column='mod_full_range'))
        # mod_invert = bool(self._get_data(row=row, column='mod_full_range'))

        # print('FFFFFFFF', mod_full_range)

        filename = 'SaltashGUIOut/'
        filename += wave
        if note != 'C':
            filename += '_' + note

        filename += '_pw' + str(pulse_width)
        if mod_type is not None:
            filename += '_' + mod_type + 'mod'
            filename += str(mod_period)
        print('filename:', filename)

        cycles = mod_period

        waveforms = {
            'sine': PyWavGenSaltash.SineWave,
            'saw': PyWavGenSaltash.PinchedSawWave,
            'square': PyWavGenSaltash.SquareWave,
            'triangle': PyWavGenSaltash.TriangleWave,
        }

        wave = waveforms[wave]()
        wave.frequency = cycles
        wave.full_range = full_range
        wave.invert = invert
        wave.phase = phase
        wave.saturate = saturate
        wave.pulse_width = pulse_width
        wave.exp = exp

        mod_wave = waveforms[mod_wave]()
        mod_wave.full_range = mod_full_range
        mod_wave.invert = mod_invert
        mod_wave.phase = mod_phase
        mod_wave.amp = mod_amp
        mod_wave.offset = mod_offset
        mod_wave.exp = mod_exp

        if mod_type == 'amp':
            wave.amplitude_mod = mod_wave
        elif mod_type == 'freq':
            wave.frequency_mod = mod_wave
        elif mod_type == 'pw':
            wave.pulse_width_mod = mod_wave

        wave.render_to_wav(length=48000 / PyWavGenSaltash.Cfreq * cycles, filename=filename + '.wav')

        file_info = md5_and_size(filename + '.wav')
        file_md5 = file_info[0]
        filesize = file_info[1]
        print('filesize = {}kB, md5 = {}'.format(round(filesize / 1024, 1), file_md5))

        mod_wave.render_to_wav(length=48000 / PyWavGenSaltash.Cfreq * cycles, filename=filename + '.mod.wav')

        os.system('open ./' + filename + '.wav')

    def menu_render_command(self):
        # for row in self.data:
        #     print('synth command', row)

        # pass

        for y in range(self.rows):
            row = self.data[y]
            print('synth test', row)
            wave = self._get_data(row=y, column='wave')
            note = self._get_data(row=y, column='note')
            mod_type = self._get_data(row=y, column='mod_type')
            mod_wave = self._get_data(row=y, column='mod_wave')
            mod_period = self._get_data(row=y, column='mod_period')
            mod_amp = self._get_data(row=y, column='mod_amp')

            s = ''
            s += wave
            if note != 'C':
                s += '_' + note
            if mod_type is not None:
                s += '_' + mod_type + 'mod'
                s += str(mod_period)
                s += '_amp' + str(mod_amp)

            s += '.wav'

            # print('{}_{}_{}mod_{}_{}'.format(note,wave,mod_type, mod_wave, mod_period))
            print(s)

            # if self._get_data(row=y, column='on'):
            # print('synth active', self.data[y])

    def add_menu_option(self, cascade, label, funct):
        '''
        easy add menu option, may replace ordered dict with lists of tuples

        edit this to allow changing existing menu options??

        '''
        if self.menu_dict is None:
            self.menu_dict = OrderedDict()
        if cascade not in self.menu_dict:
            self.menu_dict[cascade] = OrderedDict()
        self.menu_dict[cascade][label] = funct

    def init(self):

        self.add_menu_option('File', 'Open', None)
        self.add_menu_option('File', 'Save', None)
        self.add_menu_option('File', 'TestCommand', self.menu_command)

        self.add_menu_option('Synth', 'Render', self.menu_render_command)
        self.add_menu_option('Synth', 'Test1', None)
        self.add_menu_option('Synth', 'Test2', None)

        number_col_width = 3  # single numbers
        name_col_width = 10  # text
        # 5 is good for Options

        self.delete_columns()
        # self.add_column(key='on', key_type='Checkbutton', width=0)
        # self.add_column(key='name', key_type='Entry', width=10)
        self.add_column(key='wave', key_type=wavetypes.keys(), width=5)
        # self.add_column(key='lambda', key_type='Eval')
        self.add_column(key='note', key_type=note_letters)

        # self.add_column(key='on', key_type = 'Checkbutton', default_value = 0)
        self.add_column(key='full_range', key_type='Checkbutton', width=0, label='fr')
        self.add_column(key='invert', key_type='Checkbutton', label='inv', width=0)

        self.add_column(key='phase', key_type='Entry', default_value=0, width=number_col_width)
        self.add_column(key='saturate', key_type='Entry', default_value=1, width=number_col_width)
        self.add_column(key='pulse_width', key_type='Entry', default_value=0.5, width=number_col_width)
        self.add_column(key='exp', key_type='Entry', default_value=1, width=number_col_width)

        # self.add_column(key='freq', key_type='Entry')
        self.add_column(key='mod_type', key_type=[None] + mod_types)
        self.add_column(key='mod_wave', key_type=wavetypes.keys())
        self.add_column(key='mod_period', key_type='Entry', default_value=8, label='mp', width=number_col_width)
        self.add_column(key='mod_full_range', key_type='Checkbutton', label='m fr')
        self.add_column(key='mod_invert', key_type='Checkbutton', label='m inv')
        self.add_column(key='mod_phase', key_type='Entry', default_value=0, label='phase', width=number_col_width)
        self.add_column(key='mod_exp', key_type='Entry', default_value=1, label='phase', width=number_col_width)

        self.add_column(key='mod_amp', key_type='Entry', default_value=1, width=number_col_width)
        self.add_column(key='mod_offset', key_type='Entry', default_value=0, width=number_col_width)

        self.add_column(key='render', key_type='Button', function=self.button_render_command)

        # self.update_column_widths()

        print('{} keys {}'.format(self, self.keys))

        self.json_filename = 'SaltashGUIOut/MySynthGrid.json'


if __name__ == "__main__":

    master = tk.Tk()

    master.title('Saltash GUI')


    my_grid = MySynthGrid1(master)
    # my_grid = MyGrid(master)
    my_grid.__init_gui__(master)


tk.mainloop()
