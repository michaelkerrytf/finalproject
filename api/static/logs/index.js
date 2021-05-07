document.addEventListener('DOMContentLoaded', function() {

    load_logs();

    const prevBtn = document.querySelector("#previous-page-btn");
    const nextBtn = document.querySelector("#next-page-btn");

    prevBtn.addEventListener('click', () => {
        console.log('prev btn clicked');
        handlePrevNext(prevBtn);
    });

    nextBtn.addEventListener('click', () => {
        console.log('next btn clicked');
        handlePrevNext(nextBtn);
    });

});

/**
 * Used to help 'cleanup' display of log rows so that text appears 'cleanly' in 'columns'
 * @param str
 * @returns {string|*}
 */
function fix_width(str, width) {
    if (!width) {
        width = 23; // default
    }
    if (str.length === width) {
        return str;
    } else if (str.length > width) {
        return str.slice(0, width - 3) + '...';
    } else {
        const padding = Array(width - str.length).join('&nbsp;')
        return ( str + padding);
    }
}

/**
 * uses the link to fetch the appropriate logs, then delegates for display processing
 * @param link
 */
function load_logs(link) {
    const tenantPrefix = document.querySelector('#tenant-prefix').textContent;
    if (!link) {
        link = `/api/migrate/logs/${tenantPrefix}`;
    }

    console.log(`fetching logs for ${tenantPrefix}`)
    fetch(link)
        .then(response => response.json())
        .then(logs => {
            process_pagination(logs.meta);
            process_logs(logs.logs);
        });
}

/**
 * sets up prev next buttons and pagination info display
 * @param meta
 */
function process_pagination(meta) {
    const prevBtn = document.querySelector("#previous-page-btn");
    const nextBtn = document.querySelector("#next-page-btn");
    prevBtn.setAttribute('data-link', `${meta.prev}`);
    nextBtn.setAttribute('data-link', `${meta.next}`);
    if (meta.prev === meta.curr) {
        prevBtn.querySelector('button').setAttribute('disabled','disabled');
    } else {
        prevBtn.querySelector('button').removeAttribute('disabled');
    }
    if (meta.next === meta.curr) {
        nextBtn.querySelector('button').setAttribute('disabled','disabled');
    } else {
        nextBtn.querySelector('button').removeAttribute('disabled');
    }

    const paginationInfoSpan = document.querySelector('#pagination-info');
    paginationInfoSpan.innerHTML = `Displaying logs ${meta.offset + 1} - ${Math.min(meta.offset + 10, meta.count)} of ${meta.count}`;
}


/**
 * gets link from button and uses that to fetch and display the next section of logs
 * @param btn
 */
function handlePrevNext(btn) {
    const link = btn.getAttribute('data-link');
    load_logs(link);
}

/**
 * clears logs displayed and then creates new logs accordion, then populates items/rows
 * @param logs
 */
function process_logs(logs){
    const logsDiv = document.querySelector('#logs-view');
    logsDiv.innerHTML = '';
    if (logs.length > 0) {
        const logsAccordion = document.createElement('div');
        logsAccordion.classList.add('accordion');
        logsAccordion.id = 'logs-accordion';

        logs.forEach(log => {
            logsAccordion.append(create_log_row(log));
        });
        logsDiv.append(logsAccordion);
    }
}

/**
 * creates wrapper around entire accordion item
 * @param log
 * @returns {HTMLDivElement}
 */
function create_log_row(log) {
    console.log(log);

    const wrapper = document.createElement('div');
    wrapper.classList.add('accordion-item');

    wrapper.append(create_row_display_text(log));
    wrapper.append(create_body_wrapper(log));

    return wrapper;
}

/**
 * creates content displayed in accordion item header based on log entry
 * @param log
 * @returns {HTMLHeadingElement}
 */
function create_row_display_text(log) {
    const header = document.createElement('h3');
    header.classList.add('accordion-header');
    header.id = `header-${log.id}`;

    const headerButton = create_header_button(log);

    const timestampSpan = document.createElement('span');
    timestampSpan.style.marginRight = "10%";
    timestampSpan.innerHTML = log.timestamp + ' UTC';
    headerButton.append(timestampSpan);

    const leftSpan = document.createElement('span');
    let imageSrc, titleMsg;
    if(log.status === 'error') {
        imageSrc = 'red-x.png';
        titleMsg = 'Migration failed...';
    }
    if(log.status === 'invalid') {
        imageSrc = 'yellow-warning.jpg';
        titleMsg = 'Invalid Migration request';
    }
    if (log.status === 'success') {
        imageSrc = 'green-check.jpg';
        titleMsg = 'Migration succeeded!';
    }
    leftSpan.innerHTML = `By ${fix_width(log.username, 25)} -> ${fix_width(log.destination, 25)} <img src="/static/images/${imageSrc}" height="24" width="24" title="${titleMsg}">`;
    headerButton.append(leftSpan);

    header.append(headerButton);

    return header;
}

/**
 * creates accordion item wrapper - initially hidden
 * @param log
 * @returns {HTMLDivElement}
 */
function create_body_wrapper(log){
    const bodyWrapper = document.createElement('div');
    bodyWrapper.classList.add('accordion-collapse', 'collapse');
    bodyWrapper.id = `collapse-${log.id}`;
    bodyWrapper.setAttribute('data-bs-parent', '#logs-accordion');
    bodyWrapper.setAttribute('aria-labelledby', `header-${log.id}`);

    bodyWrapper.append(createBody(log));
    return bodyWrapper;
}

/**
 * creates and adds content for the initially hidden portion of the accordion item
 * @param log
 * @returns {HTMLDivElement}
 */
function createBody(log) {
    const body = document.createElement('div');
    body.classList.add('accordion-body');

    const usernameHeader = document.createElement('h6');
    usernameHeader.innerHTML = `Migrated by: ${log.username}`;
    body.append(usernameHeader);

    const userRolesHeader = document.createElement('h6');
    userRolesHeader.innerHTML = `User roles: ${log.userRoles}`;
    body.append(userRolesHeader);

    const ipAddrHeader = document.createElement('h6');
    ipAddrHeader.innerHTML = `IP Address: ${log.ipAddr}`;
    body.append(ipAddrHeader);

    const tagsHeader = document.createElement('h6');
    tagsHeader.innerHTML = `Tags: ${log.tags}`;
    body.append(tagsHeader);

    const commentHeader = document.createElement('h6');
    commentHeader.innerHTML = `Comment: ${log.comment}`;
    commentHeader.style.paddingBottom = '5px';
    commentHeader.style.borderBottom = 'solid #D3D3D3 1px';
    body.append(commentHeader);

    const requestHeader = document.createElement('h6');
    requestHeader.innerHTML = 'Request';
    body.append(requestHeader);

    const requestText = document.createElement('pre');
    requestText.innerHTML = log.requestText.replace(/(?:\r\n|\r|\n)/g, '<br>');
    + log.responseText.replace(/(?:\r\n|\r|\n)/g, '<br>');
    requestText.style.paddingBottom = '5px';
    requestText.style.borderBottom = 'solid #D3D3D3 1px';
    body.append(requestText);

    const responseHeader = document.createElement('h6');
    responseHeader.innerHTML = 'Response';
    body.append(responseHeader);

    const responseText = document.createElement('pre');
    responseText.innerHTML = log.responseText.replace(/(?:\r\n|\r|\n)/g, '<br>');
    body.append(responseText);

    return body;
}

/**
 * create section of accordion that shows on load and controls display/hide
 * @param log
 * @returns {HTMLButtonElement}
 */
function create_header_button(log) {

    const headerButton = document.createElement('button');
    headerButton.classList.add('accordion-button', 'collapsed', 'font-monospace', 'fs-6');
    headerButton.type = 'button';
    headerButton.setAttribute('data-bs-toggle', 'collapse');
    headerButton.setAttribute('data-bs-target', `#collapse-${log.id}`);
    headerButton.setAttribute('data-log', `${log.id}`);
    headerButton.setAttribute('aria-expanded', 'false');
    headerButton.setAttribute('aria-controls', `collapse-${log.id}`);

    return headerButton;
}
