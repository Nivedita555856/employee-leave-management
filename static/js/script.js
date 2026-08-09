// Employee Leave Management Portal - minimal client-side validation
//
// Just one small check: on the "Apply for Leave" form, make sure the
// To Date isn't before the From Date before the form is submitted.

document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("applyLeaveForm");
    if (!form) {
        return;
    }

    form.addEventListener("submit", function (event) {
        var fromDate = document.getElementById("from_date").value;
        var toDate = document.getElementById("to_date").value;

        if (fromDate && toDate && toDate < fromDate) {
            event.preventDefault();
            alert("'To Date' cannot be earlier than 'From Date'. Please check the dates.");
        }
    });
});
