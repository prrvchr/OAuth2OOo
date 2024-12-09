import { getParameter } from './script.js';

var url = getParameter('state', 'http://localhost:8080');
var query = location.search;
location.href = url + query
