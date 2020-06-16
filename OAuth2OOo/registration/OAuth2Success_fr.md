![Logo OAuth2](https://prrvchr.github.io/OAuth2OOo/OAuth2.png)

### Félicitations

<div id="user"></div>:

La configuration OAuth2OOo a réussi. Vous pouvez fermer cette page.

<script>
function getParameter(parameter) {
    var result = null,
        tmp = [];
    var items = location.search.substr(1).split("&");
    for (var index = 0; index < items.length; index++) {
        tmp = items[index].split("=");
        if (tmp[0] === parameter) result = decodeURIComponent(tmp[1]);
    }
    return result;
}
document.getElementById("user").innerHTML = getParameter("user");
</script>
