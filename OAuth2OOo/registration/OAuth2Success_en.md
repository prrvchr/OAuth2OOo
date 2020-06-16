![Logo OAuth2](https://prrvchr.github.io/OAuth2OOo/OAuth2.png)

### Congratulations

<div id="user"></div>:

The OAuth2OOo configuration was successful. You can close this page.

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
