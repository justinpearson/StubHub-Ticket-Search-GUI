from browsergui import *

class MinMaxSliderBlock(object): 
    '''
    Two sliders that select a range. 
    When they slide, a given callback function is called.
    If the 'max' slider is dragged below the 'min' slider,
    the 'min' slider slides along with it (and vice-versa).
    '''
    def __init__(self, name, MIN, MAX, min_init_value=None, max_init_value=None, callback=lambda: None):
        self.name = name
        self.MIN = MIN
        self.MAX = MAX
        if min_init_value is None:
            min_init_value = MIN
        if max_init_value is None:
            max_init_value = MAX
        self.min_slider   = IntegerSlider( value=min_init_value,min=MIN,max=MAX )     
        self.max_slider   = IntegerSlider( value=max_init_value,min=MIN,max=MAX )     
        self.min_text     = Text('{:.3g}'.format(MIN))
        self.max_text     = Text('{:.3g}'.format(MAX))

        def min_changed():
            print('min_changed called')
            self.min_text.text = '{:.3g}'.format(self.min_slider.value)
            if self.min_slider.value > self.max_slider.value:
                self.max_slider.value = self.min_slider.value
            callback()

        def max_changed():
            print('max_changed called')            
            self.max_text.text = '{:.3g}'.format(self.max_slider.value)            
            if self.max_slider.value < self.min_slider.value:
                self.min_slider.value = self.max_slider.value
            callback()

        
        self.min_slider.change_callback = min_changed  
        self.max_slider.change_callback = max_changed

        slider_grid = Grid([[self.min_slider],[self.max_slider]])
        slider_grid.css['display'] = 'inline'

        header = Container( Text(f'{self.name}: ['),   
                                        self.min_text,
                                        Text(' - '),
                                        self.max_text,
                                        Text(']') )

        slider_container = Container( Text('{:.3g}'.format(self.MIN)),  
                                        slider_grid,
                                        Text('{:.3g}'.format(self.MAX)) )

        slider_container.css.update({'display':'flex', 'align-items':'center'})

        self.sliders = Container(Grid([ [header], [slider_container] ],css={'display':'inline'}),css={'display':'inline'})

    def get_Element(self):
        return self.sliders
    def get_min(self):
        return self.min_slider.value
    def get_max(self):
        return self.max_slider.value
    def get_MAX(self):
        return self.MAX
    def get_MIN(self):
        return self.MIN



def main():

    def update():
        result_container = gui.body[-1]
        result_container.pop() # remove old results
        lmin = lines_slider.get_min()
        lmax = lines_slider.get_max()
        wmin = words_slider.get_min()
        wmax = words_slider.get_max()
        results = Grid([ line[wmin:wmax] for line in word_lists[lmin:lmax]])
        result_container.append(results)

    # This is the data we're manipulating:
    s = 'Chapter 1 It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters. My dear Mr Bennet, said his lady to him one day, have you heard that Netherfield Park is let at last? Mr Bennet replied that he had not. But it is, returned she; for Mrs Long has just been here, and she told me all about it. Mr Bennet made no answer'
    word_lists = [ [Text(w) for w in line.split()] for line in s.split('.') ]

    lines_slider = MinMaxSliderBlock('lines shown',0,len(word_lists), callback=update)
    words_slider = MinMaxSliderBlock('words shown',0,max(len(l) for l in word_lists), callback=update)
    
    gui = GUI()
    gui.body.append(lines_slider.get_Element())
    gui.body.append(words_slider.get_Element())
    gui.body.append(Container(Grid([[]])))
    update()

    gui.run()
                                
if __name__ == '__main__':
    main()
