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
function truncate_pad(str) {
    if (str.length === 23) {
        return str;
    } else if (str.length > 23) {
        return str.slice(0,20) + '...';
    } else {

        const padding = Array(23 - str.length).join('&nbsp;')
        return ( str + padding);
    }
}


function load_logs(link) {
    const tenantPrefix = document.querySelector('#tenant-prefix').textContent;
    if (!link) {
        link = `/api/migrate/logs/${tenantPrefix}`;
    }

    console.log(`fetching logs for ${tenantPrefix}`)
    fetch(link)
        .then(response => response.json())
        .then(logs => {
            process_logs(logs.logs);
            process_nav_btns(logs.prev, logs.curr, logs.next);
        });
}

function process_nav_btns(prev, curr, next) {
    const prevBtn = document.querySelector("#previous-page-btn");
    const nextBtn = document.querySelector("#next-page-btn");
    prevBtn.setAttribute('data-link', `${prev}`);
    nextBtn.setAttribute('data-link', `${next}`);
    if (prev === curr) {
        prevBtn.style.display = 'none';
    } else {
        prevBtn.style.display = 'inline';
    }
    if (next === curr) {
        nextBtn.style.display = 'none';
    } else {
        nextBtn.style.display = 'inline';
    }
}

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

function create_log_row(log) {
    console.log(log);

    const wrapper = document.createElement('div');
    wrapper.classList.add('accordion-item');

    wrapper.append(create_row_display_text(log));
    wrapper.append(create_body_wrapper(log));

    return wrapper;
}

function create_row_display_text(log) {
    const header = document.createElement('h2');
    header.classList.add('accordion-header');
    header.id = `header-${log.id}`;

    const headerButton = create_header_button(log);

    const timestampSpan = document.createElement('span');
    timestampSpan.style.marginRight = "10%";
    timestampSpan.innerHTML = log.timestamp;
    headerButton.append(timestampSpan);

    const leftSpan = document.createElement('span');
    leftSpan.innerHTML = `Migrated By: ${truncate_pad(log.username)}`;

    headerButton.append(leftSpan);

    header.append(headerButton);

    return header;
}

function create_body_wrapper(log){
    const bodyWrapper = document.createElement('div');
    bodyWrapper.classList.add('accordion-collapse', 'collapse');
    bodyWrapper.id = `collapse-${log.id}`;
    bodyWrapper.setAttribute('data-bs-parent', '#logs-accordion');
    bodyWrapper.setAttribute('aria-labelledby', `header-${log.id}`);

    bodyWrapper.append(create_body(log));
    return bodyWrapper;
}

function create_body(log) {
    const body = document.createElement('div');
    body.classList.add('accordion-body');

    const usernameHeader = document.createElement('h6');
    usernameHeader.innerHTML = `Created by: ${log.username}`;
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

function handlePrevNext(btn) {
    const link = btn.getAttribute('data-link');
    load_logs(link);
}
