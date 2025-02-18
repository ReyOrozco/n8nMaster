<template>
	<div :class="$style.rectangularButton">
		<slot />
	</div>
</template>

<style lang="scss" module>
.rectangularButton {
	width: 34px;
	height: 34px;
	display: flex;
	justify-content: center;
	align-items: center;
	cursor: pointer;
	border-radius: 4px;
	background-color: white;
	border: 1px solid #e6e6e6;
	box-shadow: 0px 2px 8px 0px #8c8c8c1a;

	svg {
		width: 18px;
	}
}
</style>
