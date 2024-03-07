
// Table Index Number Script
$(document).ready(function() {
    // Get the table body
    var tableBody = $('#urlTableBody');

    // Loop through each row in the table
    tableBody.find('tr').each(function(index) {
    // Add 1 to index since index is zero-based
    var serialNumber = index + 1;

    // Add the serial number to the first cell (th) in each row
    $(this).find('th:first').text(serialNumber);
    });
});
