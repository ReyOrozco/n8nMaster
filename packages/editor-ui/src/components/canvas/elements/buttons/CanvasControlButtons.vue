<script setup lang="ts">
import { Controls } from '@vue-flow/controls';
import KeyboardShortcutTooltip from '@/components/KeyboardShortcutTooltip.vue';
import { computed } from 'vue';
import { useBugReporting } from '@/composables/useBugReporting';
import { useTelemetry } from '@/composables/useTelemetry';
import { useI18n } from '@/composables/useI18n';

import { ZoomIn, ZoomOut, Undo, Focus } from 'lucide-vue-next';

const props = withDefaults(
	defineProps<{
		zoom?: number;
		showBugReportingButton?: boolean;
	}>(),
	{
		zoom: 1,
		showBugReportingButton: false,
	},
);

const emit = defineEmits<{
	'reset-zoom': [];
	'zoom-in': [];
	'zoom-out': [];
	'zoom-to-fit': [];
}>();

const { getReportingURL } = useBugReporting();
const telemetry = useTelemetry();
const i18n = useI18n();

const isResetZoomVisible = computed(() => props.zoom !== 1);

function onResetZoom() {
	emit('reset-zoom');
}

function onZoomIn() {
	emit('zoom-in');
}

function onZoomOut() {
	emit('zoom-out');
}

function onZoomToFit() {
	emit('zoom-to-fit');
}

function trackBugReport() {
	telemetry.track('User clicked bug report button in canvas', {}, { withPostHog: true });
}
</script>
<template>
	<Controls :show-zoom="false" :show-fit-view="false">
		<KeyboardShortcutTooltip :label="i18n.baseText('nodeView.zoomIn')" :shortcut="{ keys: ['+'] }">
			<RectangularIcon @click="onZoomIn">
				<ZoomIn />
			</RectangularIcon>
		</KeyboardShortcutTooltip>
		<KeyboardShortcutTooltip :label="i18n.baseText('nodeView.zoomOut')" :shortcut="{ keys: ['-'] }">
			<RectangularIcon @click="onZoomOut">
				<ZoomOut />
			</RectangularIcon>
		</KeyboardShortcutTooltip>
		<KeyboardShortcutTooltip
			v-if="isResetZoomVisible"
			:label="i18n.baseText('nodeView.resetZoom')"
			:shortcut="{ keys: ['0'] }"
		>
			<RectangularIcon @click="onResetZoom">
				<Undo />
			</RectangularIcon>
		</KeyboardShortcutTooltip>
		<KeyboardShortcutTooltip
			:label="i18n.baseText('nodeView.zoomToFit')"
			:shortcut="{ keys: ['1'] }"
		>
			<RectangularIcon @click="onZoomToFit">
				<Focus />
			</RectangularIcon>
		</KeyboardShortcutTooltip>
	</Controls>
</template>

<style lang="scss">
.vue-flow__controls {
	display: flex;
	flex-direction: column;
	gap: 10px;
	box-shadow: none;
}
</style>
