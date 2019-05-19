Django import/export, ktorý využívame na import používa na načítanie CSV súborov
knižnicu tablib, ktorá čase našej implementácie žiaľ nevie spracovať reťazce,
ohraničené úvodzovkami, ktoré obsahujú čiarku.

https://github.com/kennethreitz/tablib/issues/250
