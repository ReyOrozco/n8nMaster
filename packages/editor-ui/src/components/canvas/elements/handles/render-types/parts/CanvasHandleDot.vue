<script lang="ts" setup>
withDefaults(
	defineProps<{
		handleClasses?: string;
	}>(),
	{
		handleClasses: undefined,
	},
);
</script>

<template>
	<div :class="[$style.dot, handleClasses]" />
</template>

<style lang="scss" module>
.dot {
	width: 8px;
	height: 8px;
	border-radius: 50%;
	background: var(--color-foreground-xdark);

	&:hover {
		background: black;
	}
}
</style>
