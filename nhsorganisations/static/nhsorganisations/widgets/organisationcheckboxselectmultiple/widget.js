var showOptionsText = "Show options";
var showOptionsIconClasses = 'icon icon-fa-chevron-down fa fa-chevron-down';
var hideOptionsText = "Hide options";
var hideOptionsIconClasses = 'icon icon-fa-chevron-up fa fa-chevron-up';
var toggleVisibilityLinkHTML = '<a class="toggle-visibility" href="javascript:void(0)" onclick="toggleGroupOptionVisibility(this)" title="' + hideOptionsText + '"><span class="' + hideOptionsIconClasses + '"></span></a>';
var selectAllLinkHTML = '<a class="toggle-link check" href="javascript:void(0)" onclick="toggleAncestorCheckboxState(this, \'check\');"><span class="icon icon-fa-check fa fa-check"></span>all</a>';
var selectNoneLinkHTML = '<a class="toggle-link uncheck" href="javascript:void(0)" onclick="toggleAncestorCheckboxState(this, \'uncheck\');"><span class="icon icon-fa-check fa fa-check"></span>none</a>';
var dividerHTML = '<span class="divider"></span>';
var optionCountTotal, optionCountChecked;

function showOptions(options, toggleLink){
    options.slideDown(200);
    toggleLink.attr('title', hideOptionsText).children('.icon').attr('class', hideOptionsIconClasses);
}

function hideOptions(options, toggleLink){
    options.slideUp(200);
    toggleLink.attr('title', showOptionsText).children('.icon').attr('class', showOptionsIconClasses);
}

function toggleGroupOptionVisibility(toggleLink){
    var toggleLink = $(toggleLink);
    var options = toggleLink.siblings('ul');
    if(options.is(':visible')) hideOptions(options, toggleLink);
    else showOptions(options, toggleLink);
}

function toggleAncestorCheckboxState(elem, action){
    if(action == 'check') prop_val = 'checked';
    else prop_val = null;
    var elem = $(elem);
    elem.siblings('ul').find("input[type=checkbox]").prop('checked', prop_val);
    var options = elem.siblings('ul');
    if(action == 'check' && !options.is(':visible')) {
        showOptions(options, $(elem).siblings('.toggle-visibility'));
    }
    setTimeout(recalculateCounts, 100);
}

function countIndicatorHTML(totalCount, checkedCount){
    return '<span class="counts">(<span class="count-checked">' + checkedCount + '</span>/<span class="count-total">' + totalCount + '</span>)</span>';
}

function recalculateCounts(){
    $('.organisation_checkbox_select_multiple ul > li > ul').each(function(){
        var options = $(this);
        var checkedCount = options.find('input:checked').length;
        options.parent().find('.count-checked').html(checkedCount);
    });
}

$(function() {
    $('.organisation_checkbox_select_multiple').each(function(){
        $(this).find('ul > li > ul').each(function(){
            var options = $(this);
            optionCountTotal = options.find("input[type=checkbox]").length;
            optionCountChecked = options.find("input[type=checkbox]:checked").length;
            options.parent().prepend(toggleVisibilityLinkHTML);
            options.before(countIndicatorHTML(optionCountTotal, optionCountChecked));
            options.before(selectNoneLinkHTML);
            options.before(selectAllLinkHTML);
            options.before(dividerHTML);
            if(!options.find('input:checked').length){
                options.hide().siblings('.toggle-visibility').attr('title', showOptionsText).children('.icon').attr('class', showOptionsIconClasses);
            } 
        });
    });
    $('.organisation_checkbox_select_multiple input[type=checkbox]').change(recalculateCounts);
});
