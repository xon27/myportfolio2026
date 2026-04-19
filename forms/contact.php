<?php
declare(strict_types=1);

header('Content-Type: text/plain; charset=utf-8');

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    echo 'Method not allowed';
    exit;
}

if (($_SERVER['HTTP_X_REQUESTED_WITH'] ?? '') !== 'XMLHttpRequest') {
    http_response_code(403);
    echo 'Invalid request';
    exit;
}

$name = trim((string)($_POST['name'] ?? ''));
$email = trim((string)($_POST['email'] ?? ''));
$subject = trim((string)($_POST['subject'] ?? ''));
$message = trim((string)($_POST['message'] ?? ''));

if ($name === '' || $email === '' || $subject === '' || $message === '') {
    http_response_code(400);
    echo 'All fields are required.';
    exit;
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo 'Invalid email address.';
    exit;
}

// Block header injection in subject / display fields
$stripCrlf = static function (string $s): string {
    return str_replace(["\r", "\n", '%0a', '%0d', '%0A', '%0D'], '', $s);
};
$subject = $stripCrlf($subject);
$name = $stripCrlf($name);

$to = 'dixoncarnacete13@gmail.com'; // TODO: your inbox
$mailSubject = 'Site contact: ' . $subject;

$body = "Name: {$name}\r\n";
$body .= "Email: {$email}\r\n\r\n";
$body .= $message;

// Use an address on YOUR domain for From (helps deliverability)
$fromAddress = 'noreply@yourdomain.com'; // TODO: mailbox or no-reply on your site domain

$headers = [];
$headers[] = 'MIME-Version: 1.0';
$headers[] = 'Content-Type: text/plain; charset=utf-8';
$headers[] = 'From: ' . $fromAddress;
$headers[] = 'Reply-To: ' . $email;

if (mail($to, $mailSubject, $body, implode("\r\n", $headers))) {
    echo 'OK';
    exit;
}

http_response_code(500);
echo 'Mail could not be sent. Ask your host to enable mail() or use SMTP below.';