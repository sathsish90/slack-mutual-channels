$(document).ready(function () {
    var mutualChannelsTable = $('#mutualChannelsTable').DataTable();
    var userListTable = $('#userListTable').DataTable();
    var channelListTable = $('#channelListTable').DataTable();
    var searchResultsTable = $('#searchResultsTable').DataTable();

    function fetchUsers() {
        $.ajax({
            url: '/users',
            type: 'GET',
            success: function (users) {
                userListTable.clear().draw();  // Clear existing rows
                users.forEach(function (user) {
                    userListTable.row.add([
                        user.username,
                        user.display_name
                    ]).draw(false);
                });
            },
            error: function (xhr, status, error) {
                console.error('Error fetching users:', error);
            }
        });
    }

    function fetchChannels() {
        $.ajax({
            url: '/channels',
            type: 'GET',
            success: function (channels) {
                channelListTable.clear().draw();  // Clear existing rows
                channels.forEach(function (channel) {
                    channelListTable.row.add([
                        channel.name
                    ]).draw(false);
                });
            },
            error: function (xhr, status, error) {
                console.error('Error fetching channels:', error);
            }
        });
    }

    $('#userListBtn').on('click', function () {
        $('.section').hide();
        $('#userListSection').show();
        fetchUsers();
    });

    $('#mutualChannelsBtn').on('click', function () {
        $('.section').hide();
        $('#mutualChannelsSection').show();
    });

    $('#listChannelsBtn').on('click', function () {
        $('.section').hide();
        $('#listChannelsSection').show();
        fetchChannels();
    });

    $('#mutualChannelsForm').on('submit', function (e) {
        e.preventDefault();
        var username1 = $('#username1').val();
        var username2 = $('#username2').val();

        $.ajax({
            url: '/mutual_channels',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username1: username1, username2: username2 }),
            success: function (mutualChannels) {
                mutualChannelsTable.row.add([
                    mutualChannelsTable.rows().count() + 1,
                    username1,
                    username2,
                    mutualChannels.join(', '),
                    '<button class="edit-btn">Edit</button>',
                    '<button class="delete-btn">Delete</button>'
                ]).draw(false);
            },
            error: function (xhr, status, error) {
                console.error('Error fetching mutual channels:', error);
            }
        });
    });

    $('#mutualChannelsTable tbody').on('click', '.delete-btn', function () {
        mutualChannelsTable.row($(this).parents('tr')).remove().draw();
    });

    $('#mutualChannelsTable tbody').on('click', '.edit-btn', function () {
        var row = mutualChannelsTable.row($(this).parents('tr'));
        var data = row.data();
        $('#username1').val(data[1]);
        $('#username2').val(data[2]);
        row.remove().draw();
    });

    $('#searchBtn').on('click', function () {
        var keyword = $('#searchBox').val();

        $.ajax({
            url: '/search',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ keyword: keyword }),
            success: function (results) {
                searchResultsTable.clear().draw();  // Clear existing rows
                results.forEach(function (result, index) {
                    searchResultsTable.row.add([
                        index + 1,
                        keyword,
                        result.text,
                        result.channel,
                        result.user
                    ]).draw(false);
                });
            },
            error: function (xhr, status, error) {
                console.error('Error fetching search results:', error);
            }
        });
    });

    $.ajax({
        url: '/users',
        type: 'GET',
        success: function (users) {
            var usernames = users.map(function (user) { return user.username; });

            $('#username1').autocomplete({
                source: usernames
            });

            $('#username2').autocomplete({
                source: usernames
            });
        },
        error: function (xhr, status, error) {
            console.error('Error fetching users for autocomplete:', error);
        }
    });
});
