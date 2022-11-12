import { getParameter } from './script.js';

document.getElementById('user').innerHTML = getParameter('user', '');
document.getElementById('button').setAttribute('onclick', "window.location.href='" + getParameter('url', '') + "';");
