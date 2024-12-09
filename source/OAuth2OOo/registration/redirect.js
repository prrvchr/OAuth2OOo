import { getParameter } from './script.js';

const url = atob(getParameter('code', ''));
const query = location.search;
location.href = url + query
