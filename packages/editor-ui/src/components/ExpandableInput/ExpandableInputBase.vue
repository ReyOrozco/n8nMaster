<script setup lang="ts">
import { computed } from 'vue';

type Props = {
	modelValue: string;
	placeholder?: string;
	staticSize?: boolean;
};

const props = withDefaults(defineProps<Props>(), { staticSize: false, placeholder: '' });

const hiddenValue = computed(() => {
	let value = props.modelValue.replace(/\s/g, '.'); // force input to expand on space chars
	if (!value) {
		value = props.placeholder;
	}

	return `${value}`; // adjust for padding
});
</script>

<template>
	<!-- mock el-input element to apply styles -->
	<div :class="{ 'el-input': true, 'static-size': staticSize }" :data-value="hiddenValue">
		<slot></slot>
	</div>
</template>

<style lang="scss" scoped>
$--horiz-padding: 15px;

.el-input {
	font: inherit;

	:deep(input) {
		border: 1px solid transparent;
		padding: 0 $--horiz-padding - 2px;
		font: inherit;
	}

	&:not(.static-size)::after {
		overflow: hidden;
	}

	&:hover {
		:deep(input):not(:focus) {
			border: 1px solid var(--color-text-lighter);
		}
	}

	:deep(input):focus {
		border: 1px solid var(--color-secondary);
	}
}
</style>
