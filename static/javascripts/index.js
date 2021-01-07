var message_amount = 0;
var Ad = 0;
$(function () {
    var $messages = $('.messages-content');

    $(window).load(function () {
        $messages.mCustomScrollbar();
    });


    var namespace = '';
    console.log(namespace);
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function () {
        //console.log('connected!');
        var room_id = document.getElementsByClassName("room_id")[0].innerHTML;
        socket.emit('join', {room: room_id});
        console.log('JOIN ROOM' + room_id);
    });

    function updateScrollbar() {
        $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
            scrollInertia: 10,
            timeout: 0
        });
    }

    function setDate(time) {
        $('<div class="timestamp">' + time + '</div>').appendTo($('.message:last'));
    }

    function getQueryString(name) {
        var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");

        var r = window.location.search.substr(1).match(reg);
        if (r != null) {
            return unescape(r[2]);
        }
        return null;
    }

    function insertMessage() {
        //console.log('insertMessage');
        var msg = $('.message-input').val();
        var room_id = document.getElementsByClassName("room_id")[0].innerHTML;//$('.room_id').val();
        console.log(room_id);
        if ($.trim(msg) == '') {
            return false;
        }
        //var RoomId = getQueryString('url').split("/").slice(-1)[0];

        message_amount++;
        if (message_amount == 10){
            Ad = Math.random();
            message_amount=0;
        }

        //console.log('send Inqueiry');
        var obj = {
            msg: msg,
            room: room_id,
            //RoomId: RoomId,
            Ad: Ad
        };
        socket.emit('sendInquiry', obj);
    }


    socket.on('getInquiry', function (msg) {
        console.log(msg.Ad);
        console.log(msg.msg);
        document.getElementById('Ad').innerHTML = msg.Ad
        $('<div class="message new"><figure class="avatar"><img src="/static/mugshot/' + msg.PictureUrl + '" /></figure>' + msg.msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
        setDate(msg.time);
        $('.message-input').val(null);
        updateScrollbar();
    });


    $('.message-submit').click(function () {
        insertMessage();
    });

    $(window).on('keydown', function (e) {
        if (e.which == 13) {
            insertMessage();
            return false;
        }
    });


});
