import { getParameter } from './script.js';

document.getElementById('provider').innerHTML = getParameter('provider', '');
document.getElementById('user').innerHTML = getParameter('user', '');
