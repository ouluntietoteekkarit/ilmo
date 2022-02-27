$(document).ready(function () {
    $('input[type=radio][name=other_attributes-time]').change(function() {
        if (document.getElementById('other_attributes-time-0').checked) {
            $('#room1800').show();
            $('#room1930').hide();
        } 
        else if (document.getElementById('other_attributes-time-1').checked) {
            $('#room1800').hide();
            $('#room1930').show();
        }
        else {
            $('#room1800').hide();
            $('#room1930').hide();
        }
    });

    // THE FOLLOWING IS AN UGLY HACK BUT IT WORKS :D

    var is_set = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    $.each(JSON.parse(varatut), function(i, item) {
        if(item[0] == "18:00") {
            if(item[1] == "Pommi (Uusikatu)" && !is_set[0]) {
                $('#room1800-0').after('Pommi (Uusikatu)(varattu)');
                is_set[0] = 1;
            }
            if(item[1] == "Kuolleen miehen saari (Uusikatu)" && !is_set[1]) {
                $('#room1800-1').after('Kuolleen miehen saari (Uusikatu)(varattu)');
                is_set[1] = 1;
            }
            if(item[1] == "Temppelin kirous (Uusikatu)" && !is_set[2]) {
                $('#room1800-2').after('Temppelin kirous (Uusikatu)(varattu)');
                is_set[2] = 1;
            }
            if(item[1] == "Velhon perintö (Uusikatu)" && !is_set[3]) {
                $('#room1800-3').after('Velhon perintö (Uusikatu)(varattu)');
                is_set[3] = 1;
            }
            if(item[1] == "Murhamysteeri (Kajaaninkatu)" && !is_set[4]) {
                $('#room1800-4').after('Murhamysteeri (Kajaaninkatu)(varattu)');
                is_set[4] = 1;
            }
            if(item[1] == "Vankilapako (Kajaaninkatu)" && !is_set[5]) {
                $('#room1800-5').after('Vankilapako (Kajaaninkatu)(varattu)');
                is_set[5] = 1;
            }
            if(item[1] == "Professorin arvoitus (Kajaaninkatu)" && !is_set[6]) {
                $('#room1800-6').after('Professorin arvoitus (Kajaaninkatu)(varattu)');
                is_set[6] = 1;
            }
            if(item[1] == "The SAW (Kirkkokatu)" && !is_set[7]) {
                $('#room1800-7').after('The SAW (Kirkkokatu)(varattu)');
                is_set[7] = 1;
            }
            if(item[1] == "Alcatraz (Kirkkokatu)" && !is_set[8]) {
                $('#room1800-8').after('Alcatraz (Kirkkokatu)(varattu)');
                is_set[8] = 1;
            }
            if(item[1] == "Matka maailman ympäri (Kirkkokatu)" && !is_set[9]) {
                $('#room1800-9').after('Matka maailman ympäri (Kirkkokatu)(varattu)');
                is_set[9] = 1;
            }
        } else if(item[0] == "19:30") {
            if(item[2] == "Pommi (Uusikatu)" && !is_set[10]) {
                $('#room1930-0').after('Pommi (Uusikatu)(varattu)');
                is_set[10] = 1;
            }
            if(item[2] == "Kuolleen miehen saari (Uusikatu)" && !is_set[11]) {
                $('#room1930-1').after('Kuolleen miehen saari (Uusikatu)(varattu)');
                is_set[11] = 1;
            }
            if(item[2] == "Temppelin kirous (Uusikatu)" && !is_set[12]) {
                $('#room1930-2').after('Temppelin kirous (Uusikatu)(varattu)');
                is_set[12] = 1;
            }
            if(item[2] == "Velhon perintö (Uusikatu)" && !is_set[13]) {
                $('#room1930-3').after('Velhon perintö (Uusikatu)(varattu)');
                is_set[13] = 1;
            }
            if(item[2] == "Murhamysteeri (Kajaaninkatu)" && !is_set[14]) {
                $('#room1930-4').after('Murhamysteeri (Kajaaninkatu)(varattu)');
                is_set[14] = 1;
            }
            if(item[2] == "Vankilapako (Kajaaninkatu)" && !is_set[15]) {
                $('#room1930-5').after('Vankilapako (Kajaaninkatu)(varattu)');
                is_set[15] = 1;
            }
            if(item[2] == "Professorin arvoitus (Kajaaninkatu)" && !is_set[16]) {
                $('#room1930-6').after('Professorin arvoitus (Kajaaninkatu)(varattu)');
                is_set[16] = 1;
            }
            if(item[2] == "The SAW (Kirkkokatu)" && !is_set[17]) {
                $('#room1930-7').after('The SAW (Kirkkokatu)(varattu)');
                is_set[17] = 1;
            }
            if(item[2] == "Alcatraz (Kirkkokatu)" && !is_set[18]) {
                $('#room1930-8').after('Alcatraz (Kirkkokatu)(varattu)');
                is_set[18] = 1;
            }
            if(item[2] == "Matka maailman ympäri (Kirkkokatu)" && !is_set[19]) {
                $('#room1930-9').after('Matka maailman ympäri (Kirkkokatu)(varattu)');
                is_set[19] = 1;
            }
        }
    });

    if(!is_set[0]) {
        $('#room1800-0').after('Pommi (Uusikatu)(vapaa)');
    }
    if(!is_set[1]) {
        $('#room1800-1').after('Kuolleen miehen saari (Uusikatu)(vapaa)');
    }
    if(!is_set[2]) {
        $('#room1800-2').after('Temppelin kirous (Uusikatu)(vapaa)');
    }
    if(!is_set[3]) {
        $('#room1800-3').after('Velhon perintö (Uusikatu)(vapaa)');
    }
    if(!is_set[4]) {
        $('#room1800-4').after('Murhamysteeri (Kajaaninkatu)(vapaa)');
    }
    if(!is_set[5]) {
        $('#room1800-5').after('Vankilapako (Kajaaninkatu)(vapaa)');
    }
    if(!is_set[6]) {
        $('#room1800-6').after('Professorin arvoitus (Kajaaninkatu)(vapaa)');
    }
    if(!is_set[7]) {
        $('#room1800-7').after('The SAW (Kirkkokatu)(vapaa)');
    }
    if(!is_set[8]) {
        $('#room1800-8').after('Alcatraz (Kirkkokatu)(vapaa)');
    }
    if(!is_set[9]) {
        $('#room1800-9').after('Matka maailman ympäri (Kirkkokatu)(vapaa)');
    }
    if(!is_set[10]) {
        $('#room1930-0').after('Pommi (Uusikatu)(vapaa)');
    }
    if(!is_set[11]) {
        $('#room1930-1').after('Kuolleen miehen saari (Uusikatu)(vapaa)');
    }
    if(!is_set[12]) {
        $('#room1930-2').after('Temppelin kirous (Uusikatu)(vapaa)');
    }
    if(!is_set[13]) {
        $('#room1930-3').after('Velhon perintö (Uusikatu)(vapaa)');
    }
    if(!is_set[14]) {
        $('#room1930-4').after('Murhamysteeri (Kajaaninkatu)(vapaa)');
    }
    if(!is_set[15]) {
        $('#room1930-5').after('Vankilapako (Kajaaninkatu)(vapaa)');
    }
    if(!is_set[16]) {
        $('#room1930-6').after('Professorin arvoitus (Kajaaninkatu)(vapaa)');
    }
    if(!is_set[17]) {
        $('#room1930-7').after('The SAW (Kirkkokatu)(vapaa)');
    }
    if(!is_set[18]) {
        $('#room1930-8').after('Alcatraz (Kirkkokatu)(vapaa)');
    }
    if(!is_set[19]) {
        $('#room1930-9').after('Matka maailman ympäri (Kirkkokatu)(vapaa)');
    }

    $('#room1800-10').hide();
    $('#room1930-10').hide();
});

function myFunc(vars) {
    return vars
}