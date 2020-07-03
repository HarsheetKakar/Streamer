var $card = $('.card'),
    o = {
        38: -3,
        40: 3,
        37: 'prev',
        39: 'next'
    };

$(document).on('keyup', function (e) {
    var dir = o[e.which],
        $active = $('.active-card').removeClass('active-card'),
        i = $card.index($active);

    // Enter Key
    if (e.which === 13) {
        $active.find("button").click()
    }


    if ($active.length == 0) {
        $card.first().addClass('active-card');
        console.log()
        return;
    } else {
        if (dir === 'next' || dir === 'prev') {
            if ($active[dir]()) {
                $active[dir]().addClass('active-card');
            }
        } else {
            $card.eq(dir + i).addClass('active-card');
        }
    }
});