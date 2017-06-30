from browsergui import Button
class ToggleableButton(object):
    """docstring for ToggleableButton"""
    def __init__(self, name="My ToggleableButton", pressed=False, callback=lambda:None):
        self.name = name
        self.button = Button(name)
        self.pressed = pressed

        PRESSED     = {'background-color':'lightgray',  'border-style':'inset'}
        UNPRESSED   = {'background-color':'white',      'border-style':'outset'}

        def style_me(self): # UGH, DANGEROUS? HOW TO BETTER?
            if self.pressed:
                self.button.css.update(PRESSED) 
            else:
                self.button.css.update(UNPRESSED) 

        def onClick():
            print(f'Button {self.button.text} clicked!')
            self.pressed = not(self.pressed)
            style_me(self)
            callback()

        self.button.callback = onClick

        style_me(self)



    def get_Element(self):
        return self.button
        

def main():
    from browsergui import GUI

    def cb():
        evens = [x for x in data if x%2==0]
        print(f'Evens: {evens}')

    data = range(10)
    b = ToggleableButton(name='print ',callback=cb)
    gui = GUI(b.button).run()

if __name__ == '__main__':
    main()        