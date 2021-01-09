class Dispatcher {
    constructor(delay, func) {
        this.delay = delay;
        this.func = func
        this.timerId = null;
    }

    run() {
        this.timerID = setTimeout(() => {
            this.func(this);
        }, this.delay);
    };

    pause() {
        window.clearTimeout(this.timerID);
    }

}

let getData = function (disp) {
    $.ajax({
        url: window.location.href + '/fetch_list/',
        success: function (data) {
            $("#list-area").html(data.shopping_list);
        },
        complete: function () {
            disp.run();
        }
    });
}

const fetch = new Dispatcher(1000, getData);
fetch.run();