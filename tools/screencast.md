<!-- Firefox started (large window) -->

__`ctrl+shift+t`__

    poetry shell

-----

    clear

------

    cq-server --help

---

examples folder contains CadQuery scripts

    ls examples

---

    cat examples/.cqsignore

some of them are ignored

---

    cq-server info examples

---

starting the server

    cq-server run examples

------

__`ctrl+shift+t`__

let's try this

    firefox 127.0.0.1:5000

__`pause, pause`__

---

> click to box item (300, 400)

---

> move to rendering area (900, 400)

> drag to some other point (1100, 450)

> click to dropdown menu (100, 140)

> click to cq_tuto item (100, 240)

----

> click to grid button (300, 140)

---

> click

> click to ortho button (450, 140)

---

> click

> click to transparent button (1000, 140)

> click to black edge button (1150, 140)

> click to top view (740, 140)

> click to iso view button (600, 140)

---

__`pause, ctrl+d, ctrl+c`__

---

running with other UI options

    cq-server run --help

---

    cq-server run examples --ui-theme=dark --ui-glass --ui-hide=all

-------

__`ctrl+shift+t`__

editing scripts

    kate examples/*.py &

----

__`pause, pause, ctrl+s`__

---

__`win+left, alt+tab, win+right, ctrl+f5, alt+tab`__

---

__`ctrl+s, pgup, down, down, down, end`__

__`left, left, left, backspace, shift+4, ctrl+s`__

UI is updated as soon as a script is saved

------

__`backspace, shift+6, ctrl+s`__

------

__`ctrl+tab, ctrl+s`__

if an other file is saved, UI switches the model

------

__`alt+f4, ctrl+w, pause`__

---

trying with VSCode

    codium examples

------

__`pause, pause`__

-------

...using LivePreview extension

__`ctrl+shift+p`__

---

__`enter`__

----

    http://127.0.0.1:5000

__`enter`__

---

__`ctrl+alt+right`__

---

__`ctrl+1`__

---

__`ctrl+s`__

---

__`ctrl+s`__

-------

__`ctrl+2, ctrl+w, alt+f4`__

__`pause, ctrl+d, ctrl+c`__

---

building the showcase website

    cq-server build --help

---

    cq-server build examples docs

----------

    tree docs

---

    firefox docs/index.html

__`pause, pause, win+pgup, ctrl+f5`__

> click to stl button of cq_tuto item (680, 440)

-----

__`enter`__

> click to cq_tuto item (550, 400)

------

__`ctrl+w, pause`__

------

__`ctrl+d`__

---

__`ctrl+d`__
