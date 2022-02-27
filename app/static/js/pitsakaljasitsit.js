$(document).ready(function () {
    $("#alcohol-1").prop("checked", true);
});


$(document).ready(function () {
    $('input[type=radio][name=alcohol]').change(function () {
        if (document.getElementById('alcohol-0').checked) {
            $('#mieto').show();
            $('#vakeva').show();
            $('#viini').show();
        }
        else {
            $('#mieto').hide();
            $('#vakeva').hide();
            $('#viini').hide();
        }
    });
});
