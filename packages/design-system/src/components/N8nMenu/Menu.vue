<script lang="ts" setup>
import { ElMenu } from 'element-plus';
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import type { IMenuItem } from '../../types';
import N8nMenuItem from '../N8nMenuItem';
import { doesMenuItemMatchCurrentRoute } from '../N8nMenuItem/routerUtil';

interface MenuProps {
	type?: 'primary' | 'secondary';
	defaultActive?: string;
	collapsed?: boolean;
	transparentBackground?: boolean;
	mode?: 'router' | 'tabs';
	tooltipDelay?: number;
	items?: IMenuItem[];
	modelValue?: string;
}

const props = withDefaults(defineProps<MenuProps>(), {
	type: 'primary',
	collapsed: false,
	transparentBackground: false,
	mode: 'router',
	tooltipDelay: 300,
	items: () => [],
});
const $route = useRoute();

const emit = defineEmits<{
	select: [itemId: string];
	'update:modelValue': [itemId: string];
}>();

const activeTab = ref(props.modelValue);

const upperMenuItems = computed(() =>
	props.items.filter((item: IMenuItem) => item.position === 'top' && item.available !== false),
);

const lowerMenuItems = computed(() =>
	props.items.filter((item: IMenuItem) => item.position === 'bottom' && item.available !== false),
);

const currentRoute = computed(() => {
	return $route ?? { name: '', path: '' };
});

onMounted(() => {
	if (props.mode === 'router') {
		const found = props.items.find((item) =>
			doesMenuItemMatchCurrentRoute(item, currentRoute.value),
		);

		activeTab.value = found ? found.id : '';
	} else {
		activeTab.value = props.items.length > 0 ? props.items[0].id : '';
	}

	emit('update:modelValue', activeTab.value);
});

const onSelect = (item: IMenuItem): void => {
	if (props.mode === 'tabs') {
		activeTab.value = item.id;
	}

	emit('select', item.id);
	emit('update:modelValue', item.id);
};
</script>

<template>
	<div
		:class="{
			['menu-container']: true,
			[$style.container]: true,
			[$style.menuCollapsed]: collapsed,
			[$style.transparentBackground]: transparentBackground,
		}"
	>
		<div :class="$style.menuContent">
			<div v-if="$slots.header" :class="$style.menuHeader">
				<slot name="header"></slot>
			</div>
			<div :class="{ [$style.upperContent]: true, ['pt-xs']: $slots.menuPrefix }">
				<div v-if="$slots.menuPrefix" :class="$style.menuPrefix">
					<slot name="menuPrefix"></slot>
				</div>
				<ElMenu :default-active="defaultActive" :collapse="collapsed">
					<N8nMenuItem
						v-for="item in upperMenuItems"
						:key="item.id"
						:item="item"
						:compact="collapsed"
						:tooltip-delay="tooltipDelay"
						:mode="mode"
						:active-tab="activeTab"
						:handle-select="onSelect"
					/>
				</ElMenu>
			</div>
			<div :class="[$style.lowerContent, 'pb-2xs']">
				<slot name="beforeLowerMenu"></slot>

				<h6>Social Connectivity</h6>
				<div :class="$style.socialLinks">
					<a
						v-for="item in lowerMenuItems"
						:key="item.id"
						:class="$style.socialLinkCard"
						:href="item?.link?.href"
						:target="item?.link?.target"
					>
						<!-- For rendering Lucide icons (Vue components) -->
						<component :is="item.icon" v-if="item.icon && typeof item.icon === 'function'" />

						<!-- For rendering images -->
						<img v-else :src="item.icon" alt="Custom Icon" />

						<span>
							{{ item.label }}
						</span>
					</a>
				</div>

				<div v-if="$slots.menuSuffix" :class="$style.menuSuffix">
					<slot name="menuSuffix"></slot>
				</div>
			</div>
		</div>
	</div>
</template>

<style lang="scss" module>
.container {
	height: calc(100vh - 52px - 52px - 15px - 15px - 15px - 15px);
	display: flex;
	flex-direction: column;
	overflow: hidden;
	background-color: #f7f9fb;
	border: 1px solid #e9e9e9;
	box-shadow: 0px 0px 2px 0px #0000001f;
	padding: 16px;
	padding-bottom: 8px;
}

.menuHeader {
	display: flex;
	flex-direction: column;
	flex: 0 1 auto;
	overflow-y: auto;
}

.menuContent {
	display: flex;
	flex-direction: column;
	justify-content: space-between;
	flex: 1 1;

	& > div > :global(.el-menu) {
		background: none;
		padding: var(--menu-padding, 12px);
	}
}

.upperContent {
	ul {
		padding-top: 0 !important;
	}
}

.lowerContent {
	ul {
		padding-bottom: 0 !important;
	}

	h6 {
		margin-top: auto;
		font-weight: 400;
		font-size: 14px;
		line-height: 20px;
		letter-spacing: 0%;
		color: var(--black-40, #1c1c1c66);
		margin-bottom: 10px;
	}

	.socialLinks {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 10px;

		.socialLinkCard {
			height: 42px;
			width: 100%;
			display: flex;
			align-items: center;
			gap: 10px;
			background: #ffffff;
			border: 1px solid #e6e6e6;
			border-radius: 4px;
			padding: 12px;

			img {
				height: 18px;
			}
			svg {
				height: 20px;
			}
			span {
				font-weight: 400;
				font-size: 14px;
				line-height: 20px;
				letter-spacing: 0%;
				color: #71747a;
			}
		}
	}
}

.menuCollapsed {
	transition: width 150ms ease-in-out;
	:global(.hideme) {
		display: none !important;
	}
}

.transparentBackground {
	background-color: transparent;
}
</style>
