$(document).ready(function() {
    $('#autocomplete').on('input', function() {
        var query = $(this).val();
        if (query.length > 2) {
            $.ajax({
                url: '/autocomplete',
                data: { query: query },
                success: function(data) {
                    $('#suggestions').empty();
                    data.forEach(function(suggestion) {
                        $('<li>', {
                            'class': 'list-group-item',
                            'data-place-id': suggestion.place_id,
                            text: suggestion.description
                        }).appendTo('#suggestions');
                    });
                }
            });
        } else {
            $('#suggestions').empty();
        }
    });

    $(document).on('click', '#suggestions li', function() {
        var placeDescription = $(this).text();
        var placeId = $(this).data('place-id');
        $('#autocomplete').val(placeDescription);
        $('#place_id').val(placeId);
        $('#suggestions').empty();

        // Clear previously selected photo
        $('#selected_photo').val('');

        // Fetch details for the selected place
        $.ajax({
            url: '/get_place_details',
            data: { place_id: placeId },
            success: function(data) {
                if (data.status === 'success') {
                    $('#name_field').removeClass('d-none').find('#name').val(data.name);
                    $('#address_field').removeClass('d-none').find('#address').val(data.address);
                    $('#rating_field').removeClass('d-none').find('#rating').val(data.rating);

                    var photosDiv = $('#photos_field').removeClass('d-none').find('#photos').empty();
                    data.photos.forEach(function(photoUrl) {
                        $('<div>', { 'class': 'col-md-4' }).append(
                            $('<img>', { 'class': 'img-thumbnail m-2 photo-option', src: photoUrl, 'data-photo-url': photoUrl })
                        ).appendTo(photosDiv);
                    });

                    $('#map_location_field').removeClass('d-none').find('#map_location').attr('src', data.map_location);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching place details:', error);
            }
        });
    });

    $(document).on('click', '.photo-option', function() {
        $('.photo-option').removeClass('selected-photo');
        $(this).addClass('selected-photo');
        var photoUrl = $(this).data('photo-url');
        $('#selected_photo').val(photoUrl);
    });
});
