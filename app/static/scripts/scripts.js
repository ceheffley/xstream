$(document).ready(function () {
    // show modal
    // show modal
    $('#review-modal').on('show.bs.modal', function (event) {
        console.log("Review modal clicked!")
        const button = $(event.relatedTarget)   // Button that triggered the modal
        var keyData = button.data('source')     // Gets "<ShowId>/<UserId>" from button
        const content = button.data('content')  // Gets review text if is an edit operation
        const type = button.data('action')      // Gets "<create:edit>" depending on button
        
        const show = $('.show-title').text();   // Currently gets show title from shows.html page

        // Add "<ShowId>/<UserId>" as keyData attr to modal for later use
        $('#review-modal').attr('keyData', keyData)

        if (type === 'create') {
            // If modal for creating new review:

            // Set modal title to "Add Review of <ShowName>"
            $(this).find('.modal-title').text('Add Review of ' + show)
            // Sets Star Rating field to 5 out of 10 stars by default
            $(`input[name="star-rating"][id=5]`).prop("checked", true);
            // Add "create" as type attr to modal for later use
            $('#review-modal').attr('type', 'create')
        } else {
            // If modal for editing existing review:

            // Set modal title to "Edit Review of <ShowName>"
            $(this).find('.modal-title').text('Edit Review of ' + show)
            // Set Star Rating field to user's previous rating from "data-rating" HTML attribute
            const rating = button.data('rating')
            $(`input[name="star-rating"][id=${rating}]`).prop("checked", true);
            // Add "edit" as type attr to modal for later use
            $('#review-modal').attr('type', 'edit')
        }

        // If editing an existing review (whose review has been stored in the "data-content"
        // field), fills form with body of that review. "content" var can be replaced with any
        // variable which contains the review's text.
        if (content) {
            $(this).find('.form-control').val(content);
        } else {
            $(this).find('.form-control').val('');
        }
    });

    // Review Modal Task Submit
    $('#submit-task').click(function () {
        // Get stored "<ShowId>/<UserId>" from keyData attr
        const keyData = $('#review-modal').attr('keyData');
        // Get stored "<create:edit>" from type attr
        const type = $('#review-modal').attr('type');
        // Get currently clicked Star Rating's value attr
        const rating = parseInt($('input[name="star-rating"]:checked', '#star-rating').val())

        // Builds url as "/review/<create:edit>/<showid>/<userid>" for routes.py
        // data['description'] contains the current review text
        // data['rating'] contains the integer Star Rating
        $.ajax({
            type: 'POST',
            url: "/review/" + type + "/" + keyData,
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({
                'description': $('#review-modal').find('.form-control').val(),
                'rating': rating
            }),
            success: function (res) {
                console.log(res.response)
                location.reload();
            },
            error: function () {
                console.log('Error');
            }
        });
    });

    // Review Delete Button
    $('.remove').click(function () {
        // IMPORTANT: 'data-source="<ShowId>/<UserId>"' must be on the remove button
        // Builds url as "/review/delete/<ShowId>/<UserId>" for routes.py
        $.ajax({
            type: 'POST',
            url: '/review/delete/' + $(this).data('source'),
            success: function (res) {
                console.log(res.response)
                location.reload();
            },
            error: function () {
                console.log('Error');
            }
        });
    });

    // On search bar button press
    $('#search-value').on('keyup', function (e) {
        // Detect enter key concluding search
        if (e.key === 'Enter' || e.keyCode === 13) {
            const val = $(this).val()
            let services = []
            // Scan for <input type="checkbox"> fields, append ids to services
            $('input[type="checkbox"]:checked').each(function() {
                services.push(this.id)
            })

            // Builds url as either "/" or "/search" depending on location
            // data['keywords'] = search string
            // data['services'] = list of ServiceIds
            $.ajax({
                type: 'POST',
                url: window.location.pathname,
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify({
                    'keywords': val,
                    'services': services
                }),
                success: function (res) {
                    // On success, redirects to search page, which is built from
                    // results of AJAX from the subsequent "GET" request
                    window.location.replace("search");
                },
                error: function () {
                    console.log('Error');
                }
            });
        }
    });

    // Handle table click to navigate to shows page
    $(document).on("click", ".table tbody tr", function() {
        console.log("row clicked")
        window.location.replace("show/" + $(this).attr('id'));
    }); 

    $("#add-wt-entry-bt").click(function () {
       const ListId = document.getElementById("addWtEntry").value;
       const ShowId = document.getElementById("addEntryShowId").value;
       const Watchtype = document.getElementById("addEntryWt").value;

       $.ajax({
           type: 'POST',
           url: "/addwtentry",
           contentType: 'application/json;charset=UTF-8',
           data: JSON.stringify({ ListId: ListId, ShowId: ShowId, Watchtype: Watchtype}),
           success: function (res) {
               console.log(res);
               location.reload();
           },
           error: function () {
               console.log('Error');
           }
       });
    });

    $(".rec").click(function() {
        $.ajax({
            type: 'GET',
            url: "/search/recommendations",
            contentType: 'application/json;charset=UTF-8',
            success: function (res) {
                console.log(res);
                $(".table > thead").empty()

                $(".table > thead").append(`<th scope="col">Name</th> \
                <th scope="col">Release Year</th> \
                <th scope="col">Duration</th> \
                <th scope="col">Genre</th> \
                <th scope="col">Age Rating</th> \
                <th scope="col">Critic Ratings</th> \
                <th scope="col">Reason</th>`)

                $(".table > tbody").empty()

                res.forEach(element => {
                    $(".table > tbody").append(
                        `<tr id="${element.ShowId}"> \
                        <td class="name">${element.ShowName}</td> \
                        <td class="year">${element.ReleaseYear}</td> \
                        <td class="duration">${element.Duration}</td> \
                        <td class="year">${element.Genre}</td> \
                        <td class="age-rating">${element.AgeRating}</td> \
                        <td class="rating">${element.Ratings}</td> \
                        <td class="reason">${element.Reason}</td>
                        </tr>`
                    );
                });
            },
            error: function () {
                console.log('Error');
            }
        })
    })

});