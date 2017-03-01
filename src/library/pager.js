
// pager from http://jasonwatmore.com/post/2016/01/31/AngularJS-Pagination-Example-with-Logic-like-Google.aspx

var PagerService = [function() {
    // service implementation
    function Pager(totalItems, currentPage, pageSize) {
        // default to first page
        currentPage = currentPage || 1;

        // default page size is 12
        pageSize = pageSize || 12;

        // calculate total pages
        var totalPages = Math.ceil(totalItems / pageSize);

        // calculate start and end item indexes
        var startPage, endPage;
        if (totalPages <= 10) {
            // less than 10 total pages so show all
            startPage = 1;
            endPage = totalPages;
        } else {
            // more than 10 total pages so calculate start and end pages
            if (currentPage <= 6) {
                startPage = 1;
                endPage = 10;
            } else if (currentPage + 4 >= totalPages) {
                startPage = totalPages - 9;
                endPage = totalPages;
            } else {
                startPage = currentPage - 5;
                endPage = currentPage + 4;
            }
        }

        var startIndex = (currentPage - 1) * pageSize;
        var endIndex = Math.min(startIndex + pageSize, totalItems);

        // create an array of pages to ng-repeat in the pager control
        var pages = [];
        for(var i=0; i<=(endPage - startPage); i++) {
            pages.push(startPage + i);
        }

        // return object with all pager properties required by the view
        return {
            totalItems: totalItems,
            currentPage: currentPage,
            pageSize: pageSize,
            totalPages: totalPages,
            startIndex: startIndex,
            endIndex: endIndex,
            pages: pages
        };
    }

    // Return the factory instance.
    return( Pager );
}]

export default PagerService;
