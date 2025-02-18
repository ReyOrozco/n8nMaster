<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue';
import { useNodeCreatorStore } from '@/stores/nodeCreator.store';
import { NODE_CREATOR_OPEN_SOURCES, WORKFLOW_NODES_MODAL } from '@/constants';
import { nodeViewEventBus } from '@/event-bus';
import { useI18n } from '@/composables/useI18n';
import { useUIStore } from '@/stores/ui.store';
import RectangularIcon from '@/components/RectangularIcon.vue';
import { Plus } from 'lucide-vue-next';

const i18n = useI18n();
const nodeCreatorStore = useNodeCreatorStore();
const uiStore = useUIStore();

const isTooltipVisible = ref(false);

onMounted(() => {
	nodeViewEventBus.on('runWorkflowButton:mouseenter', onShowTooltip);
	nodeViewEventBus.on('runWorkflowButton:mouseleave', onHideTooltip);
});

onBeforeUnmount(() => {
	nodeViewEventBus.off('runWorkflowButton:mouseenter', onShowTooltip);
	nodeViewEventBus.off('runWorkflowButton:mouseleave', onHideTooltip);
});

function onShowTooltip() {
	isTooltipVisible.value = true;
}

function onHideTooltip() {
	isTooltipVisible.value = false;
}

function onClick() {
	nodeCreatorStore.openNodeCreatorForTriggerNodes(
		NODE_CREATOR_OPEN_SOURCES.TRIGGER_PLACEHOLDER_BUTTON,
	);
	uiStore.openModal(WORKFLOW_NODES_MODAL);
}
</script>
<template>
	<div ref="container" :class="$style.addNodes" data-test-id="canvas-add-button">
		<N8nTooltip
			placement="top"
			:visible="isTooltipVisible"
			:disabled="nodeCreatorStore.showScrim"
			:popper-class="$style.tooltip"
			:show-after="700"
		>
			<div :class="$style.nodeBox" @click="onClick">
				<RectangularIcon data-test-id="canvas-plus-button">
					<Plus />
				</RectangularIcon>
				<div :class="$style.nodeText">
					<h3
						:class="$style.label"
						v-text="i18n.baseText('nodeView.canvasAddButton.addFirstStep')"
					/>
					<span>Click to get started</span>
				</div>
			</div>

			<template #content>
				{{ i18n.baseText('nodeView.canvasAddButton.addATriggerNodeBeforeExecuting') }}
			</template>
		</N8nTooltip>
	</div>
</template>

<style lang="scss" module>
.addNodes {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	width: 100px;
	height: 100px;

	&:hover .button svg path {
		fill: var(--color-primary);
	}
}

.nodeBox {
	min-width: 100px;
	min-height: 64px;
	padding: 16px;
	display: flex;
	justify-content: center;
	align-items: center;
	gap: 8px;
	cursor: pointer;
	border-radius: 6px;
	background-color: white;
	border: 1px solid #e6e6e6;
	box-shadow: 0px 2px 8px 0px #8c8c8c1a;

	.nodeText {
		width: max-content;

		h3 {
			font-size: 12px;
			font-weight: 500;
		}
		span {
			font-size: 10px;
			font-weight: 400;
			color: #828282;
		}
	}
}
</style>
