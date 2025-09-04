<script lang="ts">
	import { getVersionUpdates } from '$lib/apis';
	import { getOllamaVersion } from '$lib/apis/ollama';
	import { WEBUI_BUILD_HASH, WEBUI_VERSION } from '$lib/constants';
	import { WEBUI_NAME, config, showChangelog } from '$lib/stores';
	import { compareVersion } from '$lib/utils';
	import { onMount, getContext } from 'svelte';

	import Tooltip from '$lib/components/common/Tooltip.svelte';

	const i18n = getContext('i18n');

	let ollamaVersion = '';

	let updateAvailable = null;
	let version = {
		current: '',
		latest: ''
	};

	const checkForVersionUpdates = async () => {
		updateAvailable = null;
		version = await getVersionUpdates(localStorage.token).catch((error) => {
			return {
				current: WEBUI_VERSION,
				latest: WEBUI_VERSION
			};
		});

		console.log(version);

		updateAvailable = compareVersion(version.latest, version.current);
		console.log(updateAvailable);
	};

	onMount(async () => {
		ollamaVersion = await getOllamaVersion(localStorage.token).catch((error) => {
			return '';
		});

		if ($config?.features?.enable_version_update_check) {
			checkForVersionUpdates();
		}
	});
</script>

<div id="tab-about" class="flex flex-col h-full justify-between space-y-3 text-sm mb-6">
	<div class=" space-y-3 overflow-y-scroll max-h-[28rem] lg:max-h-full">
		<div>
			<div class=" mb-2.5 text-sm font-medium flex space-x-2 items-center">
				<div>
					{$WEBUI_NAME}
					{$i18n.t('Version')}
				</div>
			</div>
			<div class="flex w-full justify-between items-center">
				<div class="flex flex-col text-xs text-gray-700 dark:text-gray-200">
					<div class="flex gap-1">
						<Tooltip content={WEBUI_BUILD_HASH}>
							v{WEBUI_VERSION}
						</Tooltip>

						<!-- {#if $config?.features?.enable_version_update_check}
							<a
								href="https://github.com/open-webui/open-webui/releases/tag/v{version.latest}"
								target="_blank"
							>
								{updateAvailable === null
									? $i18n.t('Checking for updates...')
									: updateAvailable
										? `(v${version.latest} ${$i18n.t('available!')})`
										: $i18n.t('(latest)')}
							</a>
						{/if} -->
					</div>

					<!-- <button
						class=" underline flex items-center space-x-1 text-xs text-gray-500 dark:text-gray-500"
						on:click={() => {
							showChangelog.set(true);
						}}
					>
						<div>{$i18n.t("See what's new")}</div>
					</button> -->
				</div>

				<!-- {#if $config?.features?.enable_version_update_check}
					<button
						class=" text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-lg font-medium"
						on:click={() => {
							checkForVersionUpdates();
						}}
					>
						{$i18n.t('Check for updates')}
					</button>
				{/if} -->
			</div>
		</div>

		{#if ollamaVersion}
			<hr class=" border-gray-100 dark:border-gray-850" />

			<div>
				<div class=" mb-2.5 text-sm font-medium">{$i18n.t('Ollama Version')}</div>
				<div class="flex w-full">
					<div class="flex-1 text-xs text-gray-700 dark:text-gray-200">
						{ollamaVersion ?? 'N/A'}
					</div>
				</div>
			</div>
		{/if}

		<hr class=" border-gray-100 dark:border-gray-850" />

		<!-- {#if $config?.license_metadata}
			<div class="mb-2 text-xs">
				{#if !$WEBUI_NAME.includes('Open WebUI')}
					<span class=" text-gray-500 dark:text-gray-300 font-medium">{$WEBUI_NAME}</span> -
				{/if}

				<span class=" capitalize">{$config?.license_metadata?.type}</span> license purchased by
				<span class=" capitalize">{$config?.license_metadata?.organization_name}</span>
			</div>
		{:else}
			<div class="flex space-x-1">
				<a href="https://discord.gg/5rJgQTnV4s" target="_blank">
					<img
						alt="Discord"
						src="https://img.shields.io/badge/Discord-Open_WebUI-blue?logo=discord&logoColor=white"
					/>
				</a>

				<a href="https://twitter.com/OpenWebUI" target="_blank">
					<img
						alt="X (formerly Twitter) Follow"
						src="https://img.shields.io/twitter/follow/OpenWebUI"
					/>
				</a>

				<a href="https://github.com/open-webui/open-webui" target="_blank">
					<img
						alt="Github Repo"
						src="https://img.shields.io/github/stars/open-webui/open-webui?style=social&label=Star us on Github"
					/>
				</a>
			</div>
		{/if} -->

		<!-- <div class="mt-2 text-xs text-gray-400 dark:text-gray-500">
			Emoji graphics provided by
			<a href="https://github.com/jdecked/twemoji" target="_blank">Twemoji</a>, licensed under
			<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">CC-BY 4.0</a>.
		</div> -->

		<div>
			<pre
				class="text-xs text-gray-400 dark:text-gray-500">Copyright (c) {new Date().getFullYear()} <a
					href="https://houmoai.com"
					target="_blank"
					class="underline">LanyueChat (houmoai.com)</a
				>

LanyueChat 是一个开源的通用型大语言模型（LLM）图形界面平台，旨在为开发者、研究者和企业用户提供简洁、功能丰富的界面，用于交互、测试和部署各种 LLM 模型。它支持多种本地和远程部署方式，并通过模块化架构，方便用户根据自身需求灵活接入不同的模型与服务。

系统基于现代前后端分离架构设计，前端采用响应式界面，支持多轮对话、函数调用（Function Calling）、RAG 检索问答、多模型切换、角色扮演等功能，适合从开发调试到业务集成的各类使用场景。后端则集成了 API 代理、中间件、自定义插件系统、SSE 流式响应机制，以及对模型使用统计、访问权限的管理等能力。

LanyueChat 支持的模型涵盖主流开源与商业大语言模型，具体包括：

1. Qwen 系列（通义千问）：如 qwen2-7b、qwen2.5-7b、qwen2.5-14b、qwen3-8b 等，具备较强中文能力与函数调用能力。

2. DeepSeek 系列：如 deepseek-7b、deepseek-14b，擅长代码生成与中英混合任务。

3. 图像生成模型：如 Stable Diffusion XL、SD3，可用于文本生成图像的扩展能力。

用户可通过配置文件或 UI 面板轻松完成模型接入与切换，还支持 API Key 管理、自定义模型参数调整等操作。

总之，LanyueChat 兼顾易用性与专业性，是一个集模型接入、界面交互、扩展开发于一体的强大平台，广泛适用于 AI 应用的研发、测试与部署。
</pre>
		</div>

		<!-- <div class="mt-2 text-xs text-gray-400 dark:text-gray-500">
			{$i18n.t('Created by')}
			<a
				class=" text-gray-500 dark:text-gray-300 font-medium"
				href="https://github.com/tjbck"
				target="_blank">Timothy J. Baek</a
			>
		</div> -->
	</div>
</div>
