$(document).ready(function () {
    $("#login-bt").click(function () {
        var username = document.getElementById("uname").value;
        var password = document.getElementById("pass").value;
        $.ajax({
            type: 'POST',
            url: '/login',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({ username: username, password: password }),
            success: function (res) {
                console.log(res.response)
                window.location.replace("/")
            },
            error: function () {
                console.log('Error');
            }
        });
    });

    $("#newuser-bt").click(function () {
        var username = document.getElementById("uname").value;
        var password = document.getElementById("pass").value;
        var email = document.getElementById("email").value;
        var age = document.getElementById("age").value;
        var name = document.getElementById("name").value;
        var services = []
        // Scan for <input type="checkbox"> fields, append ids to services
        $('input[type="checkbox"]:checked').each(function() {
            services.push(this.id)
        })
        $.ajax({
            type: 'POST',
            url: '/new',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({ username: username, password: password, email: email, age: age, name: name, services: services}),
            success: function (res) {
                console.log(res);
                $('#replaceme').html(res);
                // window.location.replace('/new/2');
            },
            error: function () {
                console.log('Error');
            }
        });
    });

    $("#save-bt").click(function () {
        var username = document.getElementById("uname").value;
        var password = document.getElementById("pass").value;
        var email = document.getElementById("email").value;
        var age = document.getElementById("age").value;
        var name = document.getElementById("name").value;
        if(username == "" || username == null || password == "" || password == null) {
            window.location.replace("/user/" + encodeURIComponent(username));
            return;
        }
        var services = []
        // Scan for <input type="checkbox"> fields, append ids to services
        $('input[type="checkbox"]:checked').each(function() {
            services.push(this.id)
        })
        $.ajax({
            type: 'POST',
            url: "/user/" + encodeURIComponent(username),
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({ username: username, password: password, email: email, age: age, name: name, services:services}),
            success: function (res) {
                console.log(res);
                window.location.replace("/user/" + encodeURIComponent(username));
            },
            error: function () {
                console.log('Error');
            }
        });
    });

    $('#edit-watchlist-modal').on('show.bs.modal', function (event) {
        const button = $(event.relatedTarget) // Button that triggered the modal
        const listid = button.data('source') // Extract info from data-* attributes
        const listname = button.data('content')

        const modal = $(this)
        modal.find('.modal-title').text('Edit Watchlist' + listid)
        //$('#edit-show-form-display').attr('showID', showID)

        document.getElementById("editListName").value = listname;
        document.getElementById("editListId").value = listid;
    })

    $("#edit-watchlist-bt").click(function () {
        const listname = document.getElementById("editListName").value;
        const listid = document.getElementById("editListId").value;
        $.ajax({
            type: 'POST',
            url: "/editwt",
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({ ListName: listname, ListId: listid}),
            success: function (res) {
                console.log(res);
                location.reload();
            },
            error: function () {
                console.log('Error');
            }
        });
    });

    $("#add-watchlist-bt").click(function () {
        const listname = document.getElementById("addListName").value;
        $.ajax({
            type: 'POST',
            url: "/addwt",
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({ ListName: listname}),
            success: function (res) {
                console.log(res);
                location.reload();
            },
            error: function () {
                console.log('Error');
            }
        });
    });


    $('.remove').click(function () {
        const remove = $(this);
        $.ajax({
            type: 'POST',
            url: '/deletewt',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({ ListId: remove.data('source')}),
            success: function (res) {
                console.log(res.response)
                location.reload();
            },
            error: function () {
                console.log('Error');
            }
        });
    });

    $('.remove-show').click(function () {
        const remove = $(this);
        $.ajax({
            type: 'POST',
            url: '/deletewtentry',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({ ListId: remove.data('source'), ShowId: remove.data('content')}),
            success: function (res) {
                console.log(res.response)
                location.reload();
            },
            error: function () {
                console.log('Error');
            }
        });
    });

    $('#edit-wt-show-modal').on('show.bs.modal', function (event) {
        const button = $(event.relatedTarget) // Button that triggered the modal
        const ListId = button.data('source') // Extract info from data-* attributes
        const ShowId = button.data('content')
        const Watchtype = button.data('watchtype')

        document.getElementById("editListIdWt").value = ListId;
        document.getElementById("editShowIdWt").value = ShowId;
        document.getElementById("editWatchtype").value = Watchtype;
        document.getElementById("entryList").value = ListId;

    })

    $("#edit-wt-show-bt").click(function () {
       const ListId = document.getElementById("editListIdWt").value;
       const newListId = document.getElementById("entryList").value;
       const ShowId = document.getElementById("editShowIdWt").value;
       const Watchtype = document.getElementById("editWatchtype").value;

       $.ajax({
           type: 'POST',
           url: "/editwtentry",
           contentType: 'application/json;charset=UTF-8',
           data: JSON.stringify({ ListId: ListId, ShowId: ShowId, Watchtype: Watchtype, newListId: newListId}),
           success: function (res) {
               console.log(res);
               location.reload();
           },
           error: function () {
               console.log('Error');
           }
       });
    });


});