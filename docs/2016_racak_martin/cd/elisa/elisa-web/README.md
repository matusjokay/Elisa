# Elisa web client

Elisa is a prototype timetabling system for schools and universities. This is a
reference web client implementation which works with Elisa server.

This project was set up with the help of
[elm-webpack-starter](https://github.com/elm-community/elm-webpack-starter).

## Development

Node.js 6.10 (or higher) is required. Install all dependencies using the handy
`reinstall` script:

```
npm run reinstall
```

This does a clean (re)install of all npm and elm packages including a global Elm
toolchain.

We advise to use [elm-format](https://github.com/avh4/elm-format) for automatic
code formatting (must be installed separately).

### Serve locally

```
npm start
```

* Access app at [`http://localhost:8080/`](http://localhost:8080/)
* Browser will refresh automatically on any file changes


### Build & bundle for production

```
npm run build
```

Files are saved into `dist` folder.

## License

Elisa web client is licensed under the GPLv3. See LICENSE for more details.
