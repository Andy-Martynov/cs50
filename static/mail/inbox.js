document.addEventListener('DOMContentLoaded', function() {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);

    document.querySelector('#compose-submit').addEventListener('click', () => send_email());

    // By default, load the inbox

    load_mailbox('inbox');

});

function compose_email() {

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
    document.querySelector('#email-details').style.display = 'none';

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
}

async function load_mailbox(mailbox) {

    html = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    emails = await fetch('/mail/emails/'+mailbox)
    .then (response => response.json());

    for (i in emails) {
        if (emails[i].read == true) {
            background = 'secondary';
        } else {
            background = 'light';
        }
        html = html + `<div id="email_${emails[i].id}" onclick="show_email(${emails[i].id})" class="email alert alert-${background} border border-secondary rounded">`;
        html = html + `[${emails[i].id}] <b>from : </b> ${emails[i].sender}, <b>to : </b> ${emails[i].recipients}, <b>subject : </b> ${emails[i].subject} (${emails[i].timestamp})`;
        html = html + `</div>`;
    }

    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-details').style.display = 'none';

    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML = html;
}


function send_email() {

    recipients = document.querySelector('#compose-recipients').value;
    subject = document.querySelector('#compose-subject').value;
    body = document.querySelector('#compose-body').value;

    fetch('/mail/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: recipients,
            subject: subject,
            body: body
            })
        })
    .then((response) => response.json())
    .then(result => {
        // Print result
        console.log(result);
    })
    .then(load_mailbox('sent'));
}

function show_email(id) {

    fetch(`/mail/emails/${id}`)
    .then(response => response.json())
    .then(email => {

        let html = `<p><b>From : </b>${email.sender}</p>`;
        html += `<p><b>To : </b>${email.recipients}</p>`;
        html += `<p><b>Sent : </b>${email.timestamp}</p>`;
        html += `<p><b>Subject : </b>${email.subject}</p>`;
        html += `<p><b>`;
        if (email.archived == true) {
            html += `Archived `;
        }
        if (email.read == true) {
            html += `Read`;
        }
        html += `</b><hr>`;
        html += `<button class="btn btn-sm btn-outline-primary" id="reply" onclick="reply('${email.sender}', '${email.subject}', '${email.body}', '${email.timestamp}')">Reply</button>`;
        if (email.archived == true) {
            html += `<button class="btn btn-sm btn-outline-primary" id="archive" onclick="archive_email(${email.id}, false)">UnArchive</button>`;
        } else {
            html += `<button class="btn btn-sm btn-outline-primary" id="archive" onclick="archive_email(${email.id}, true)">Archive</button>`;
        }
        html += `<hr>`;
        html += `<p>${email.body}</p>`;
        html += `<hr>`;

        document.querySelector('#email-details').innerHTML =html;
    });
    fetch(`/mail/emails/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
    })
    .then(response => response.text())
    .then(error => {
        console.log(error);
    });
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-details').style.display = 'block';
}

function archive_email(id, archive) {

    fetch(`/mail/emails/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: archive
        })
    })
    .then(response => response.text())
    .then(error => {
        console.log(error);
    })
    .then(load_mailbox('inbox'));
}

function reply(sender, subject, body, timestamp) {

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
    document.querySelector('#email-details').style.display = 'none';

    if (subject.substring(0,3) != 'Re:') {
        subject = 'Re: ' + subject;
    }

    let first_line = `


On ${timestamp} ${sender} wrote:

`;
    body = first_line + body;

    // Set composition fields
    document.querySelector('#compose-recipients').value = sender;
    document.querySelector('#compose-subject').value = subject;
    document.querySelector('#compose-body').value = body;

}



