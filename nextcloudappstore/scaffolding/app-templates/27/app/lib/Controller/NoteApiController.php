<?php

declare(strict_types=1);
// SPDX-FileCopyrightText: {{ app.author_name }} <{{ app.author_mail }}>
// SPDX-License-Identifier: {{ app.license }}

namespace OCA\{{ app.namespace }}\Controller;

use OCA\{{ app.namespace }}\AppInfo\Application;
use OCA\{{ app.namespace }}\Service\NoteService;
use OCP\AppFramework\ApiController;
use OCP\AppFramework\Http\DataResponse;
use OCP\IRequest;

class NoteApiController extends ApiController {
	private NoteService $service;
	private ?string $userId;

	use Errors;

	public function __construct(IRequest $request,
		NoteService $service,
		?string $userId) {
		parent::__construct(Application::APP_ID, $request);
		$this->service = $service;
		$this->userId = $userId;
	}

	/**
	 * @CORS
	 * @NoCSRFRequired
	 * @NoAdminRequired
	 */
	public function index(): DataResponse {
		return new DataResponse($this->service->findAll($this->userId));
	}

	/**
	 * @CORS
	 * @NoCSRFRequired
	 * @NoAdminRequired
	 */
	public function show(int $id): DataResponse {
		return $this->handleNotFound(function () use ($id) {
			return $this->service->find($id, $this->userId);
		});
	}

	/**
	 * @CORS
	 * @NoCSRFRequired
	 * @NoAdminRequired
	 */
	public function create(string $title, string $content): DataResponse {
		return new DataResponse($this->service->create($title, $content,
			$this->userId));
	}

	/**
	 * @CORS
	 * @NoCSRFRequired
	 * @NoAdminRequired
	 */
	public function update(int $id, string $title,
		string $content): DataResponse {
		return $this->handleNotFound(function () use ($id, $title, $content) {
			return $this->service->update($id, $title, $content, $this->userId);
		});
	}

	/**
	 * @CORS
	 * @NoCSRFRequired
	 * @NoAdminRequired
	 */
	public function destroy(int $id): DataResponse {
		return $this->handleNotFound(function () use ($id) {
			return $this->service->delete($id, $this->userId);
		});
	}
}
