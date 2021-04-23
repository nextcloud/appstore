<?php

namespace OCA\{{ app.namespace }}\Tests\Unit\Controller;

use Test\TestCase;

use OCP\AppFramework\Http\TemplateResponse;

use OCA\{{ app.namespace }}\Controller\PageController;


class PageControllerTest extends TestCase {
	private $controller;
	private $userId = 'john';

	public function setUp() {
		$request = $this->getMockBuilder('OCP\IRequest')->getMock();

		$this->controller = new PageController(
			'{{ app.id }}', $request, $this->userId
		);
	}

	public function testIndex() {
		$result = $this->controller->index();

		$this->assertEquals('index', $result->getTemplateName());
		$this->assertTrue($result instanceof TemplateResponse);
	}

}
