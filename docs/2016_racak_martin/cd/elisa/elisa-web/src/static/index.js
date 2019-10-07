// pull in desired CSS/SASS files
require('./styles/main.scss');
var $ = jQuery = require('../../node_modules/jquery/dist/jquery.js'); // <--- remove if jQuery not needed
require('../../node_modules/bootstrap-sass/assets/javascripts/bootstrap.js'); // <--- remove if Bootstrap's JS not needed

var Elm = require('../elm/Main');

var node = document.getElementById('main');
var token = localStorage.getItem('token');
var app = Elm.Main.embed(node, {
    token: token
});
app.ports.storeToken.subscribe(function(token) {
    localStorage.setItem('token', token);
});
app.ports.removeToken.subscribe(function() {
    localStorage.removeItem('token');
});
