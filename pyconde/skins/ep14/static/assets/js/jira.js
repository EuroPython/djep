(function($) {
    window.ATL_JQ_PAGE_PROPS = {
        "triggerFunction": function(showCollectorDialog) {
            $("#get-in-touch").click(function(e) {
                e.preventDefault();
                showCollectorDialog();
            });
        }
    };
})(jQuery);