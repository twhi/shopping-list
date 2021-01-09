$(document).on('click', '.sort-title', function(e) {
    var table = $(this).parents('table').eq(0)
    var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()))

    var allSortIcons = table.find('i');
    allSortIcons.removeClass('fa-sort fa-sort-down fa-sort-up');

    var sortIcon = $(this).find('i');

    var otherSortIcons = allSortIcons.not(sortIcon);
    otherSortIcons.addClass('fa-sort');

    this.asc = !this.asc
    if (!this.asc) {
        rows = rows.reverse()
        sortIcon.addClass('fa-sort-up');
    }
    else {
        sortIcon.addClass('fa-sort-down');
    }

    for (var i = 0; i < rows.length; i++) {
        table.append(rows[i])
    }
})

function comparer(index) {
    return function(a, b) {
        var valA = getCellValue(a, index),
            valB = getCellValue(b, index)
        return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB)
    }
}

function getCellValue(row, index) {
    return $(row).children('td').eq(index).text()
}