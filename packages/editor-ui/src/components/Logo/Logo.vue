<script setup lang="ts">
import type { FrontendSettings } from '@n8n/api-types';
import { computed, onMounted, useCssModule, useTemplateRef } from 'vue';
import { useFavicon } from '@vueuse/core';

import LogoIcon from './logo-icon-2.svg';

const props = defineProps<
	(
		| {
				location: 'authView';
		  }
		| {
				location: 'sidebar';
				collapsed: boolean;
		  }
	) & {
		releaseChannel: FrontendSettings['releaseChannel'];
	}
>();

const { location, releaseChannel } = props;

const showReleaseChannelTag = computed(() => {
	if (releaseChannel === 'stable') return false;
	if (location === 'authView') return true;
	return !props.collapsed;
});

const showLogoText = computed(() => {
	if (location === 'authView') return true;
	return !props.collapsed;
});

const $style = useCssModule();
const containerClasses = computed(() => {
	if (location === 'authView') {
		return [$style.logoContainer, $style.authView];
	}
	return [
		$style.logoContainer,
		$style.sidebar,
		props.collapsed ? $style.sidebarCollapsed : $style.sidebarExpanded,
	];
});

const svg = useTemplateRef<{ $el: Element }>('logo');
onMounted(() => {
	if (releaseChannel === 'stable' || !('createObjectURL' in URL)) return;

	const logoEl = svg.value!.$el;

	// Reuse the SVG as favicon
	const blob = new Blob([logoEl.outerHTML], { type: 'image/svg+xml' });
	useFavicon(URL.createObjectURL(blob));
});
</script>

<template>
	<div :class="containerClasses" data-test-id="flowstate-logo">
		<LogoIcon :class="$style.logo" ref="logo" />
		<h3 v-if="showLogoText" :class="$style.logoText">flowstate</h3>
		<div v-if="showReleaseChannelTag" size="small" round :class="$style.releaseChannelTag">
			{{ releaseChannel }}
		</div>
	</div>
</template>

<style lang="scss" module>
.logoContainer {
	display: flex;
	justify-content: center;
	align-items: center;
}

.logoText {
	margin-left: 7px;
	font-size: 12px;
}

.releaseChannelTag {
	color: var(--color-text-dark);
	padding: var(--spacing-5xs) var(--spacing-4xs);
	background-color: var(--color-background-base);
	border: 1px solid var(--color-foreground-base);
	border-radius: var(--border-radius-base);
	font-size: var(--font-size-4xs);
	font-weight: var(--font-weight-bold);
	text-transform: capitalize;
	line-height: var(--font-line-height-regular);
	height: var(--spacing-s);
	margin-left: 4px;
}

.authView {
	transform: scale(2);
	margin-bottom: var(--spacing-xl);
}

.sidebar {
	transform: scale(1.3);
}

.sidebarExpanded .logo {
	margin-left: var(--spacing-xs);
}

.sidebarCollapsed .logo {
	width: 40px;
	height: 30px;
	padding: 0 var(--spacing-4xs);
}
</style>
