/**
 * Created by horace on 16-7-28.
 */

if (typeof jQuery === "undefined") {
  throw new Error("This JS requires jQuery");
}

$(document).ready(function() {
    $("#set_all").click(function () {
        $("label>input").prop("checked", true)
    });
    $("#unset_all").click(function () {
        $("label>input").prop("checked", false)
    });
});