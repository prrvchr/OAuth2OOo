import { getParameter } from './script.js';

document.getElementById('user').innerHTML = getParameter('user', '');
