<?php
declare(strict_types=1);
// SPDX-FileCopyrightText: {{ app.author_name }} <{{ app.author_mail }}>
// SPDX-License-Identifier: {{ app.license }}

namespace OCA\{{ app.namespace }}\AppInfo;

use OCP\AppFramework\App;

class Application extends App {
	public const APP_ID = '{{ app.id }}';

	public function __construct() {
		parent::__construct(self::APP_ID);
	}
}
