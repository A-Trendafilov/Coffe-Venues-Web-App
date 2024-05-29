$(document).ready(function() {
    // Handle input event on the autocomplete field
    $('#autocomplete').on('input', function() {
        var query = $(this).val();
        if (query.length > 2) {
            // Fetch autocomplete suggestions
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

    // Handle click event on suggestion items
    $(document).on('click', '#suggestions li', function() {
        var placeId = $(this).data('place-id');
        $('#autocomplete').val($(this).text());
        $('#place_id').val(placeId);
        $('#suggestions').empty();
        $('#selected_photo').val('');

        // Fetch place details
        $.ajax({
            url: '/get_place_details',
            data: { place_id: placeId },
            success: function(data) {
                if (data.status === 'success') {
                    $('#name_field').removeClass('d-none').find('#name').val(data.name);
                    $('#address_field').removeClass('d-none').find('#address').val(data.address);
                    $('#rating_field').removeClass('d-none').find('#rating').val(data.rating);

                    $('#lat').val(data.lat);
                    $('#lng').val(data.lng);

                    var photosDiv = $('#photos_field').removeClass('d-none').find('#photos').empty();
                    data.photos.forEach(function(photoReference) {
                        // Fetch the photo URL from the backend
                        $.ajax({
                            url: '/get_photo_url',
                            data: { photo_reference: photoReference },
                            success: function(photoData) {
                                $('<div>', { 'class': 'col-12 col-sm-6 col-md-4 col-lg-3 photo-container' }).append(
                                    $('<img>', { 'class': 'img-thumbnail m-2 photo-option', src: photoData.photo_url, 'data-photo-reference': photoReference })
                                ).appendTo(photosDiv);
                            }
                        });
                    });

                    // Fetch and display the map image
                    fetchMapImage(data.lat, data.lng);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching place details:', error);
            }
        });
    });

    // Handle click event on photo options
    $(document).on('click', '.photo-option', function() {
        $('.photo-option').removeClass('selected-photo');
        $(this).addClass('selected-photo');
        var photoReference = $(this).data('photo-reference');
        $('#selected_photo').val(photoReference);
    });

    // Handle form submission
    $('#placeForm').submit(function(event) {
        event.preventDefault();

        var formData = $(this).serialize();
        $.ajax({
            type: 'POST',
            url: '/add_place',
            data: formData,
            success: function(response) {
                window.location.href = '/';
            },
            error: function(xhr, status, error) {
                console.error('Error adding place:', error);
            }
        });
    });
});

// Function to fetch and display the map image
function fetchMapImage(lat, lng) {
    $.ajax({
        url: '/get_map',
        data: { lat: lat, lng: lng },
        success: function(data) {
            $('#map_location_field').removeClass('d-none').find('#map_location').attr('src', 'data:image/jpeg;base64,' + data.map_image);
        },
        error: function(xhr, status, error) {
            console.error('Error fetching map image:', error);
        }
    });
}
