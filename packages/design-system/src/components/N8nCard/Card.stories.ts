import type { StoryFn } from '@storybook/vue3';

import N8nCard from './Card.vue';
import N8nButton from '../N8nButton/Button.vue';
import N8nIcon from '../N8nIcon/Icon.vue';
import N8nText from '../N8nText/Text.vue';

export default {
	title: 'Atoms/Card',
	component: N8nCard,
};

export const Default: StoryFn = (args, { argTypes }) => ({
	setup: () => ({ args }),
	props: Object.keys(argTypes),
	components: {
		N8nCard,
	},
	template: '<flowstate-card v-bind="args">This is a card.</flowstate-card>',
});

export const Hoverable: StoryFn = (args, { argTypes }) => ({
	setup: () => ({ args }),
	props: Object.keys(argTypes),
	components: {
		N8nCard,
		N8nIcon,
		N8nText,
	},
	template: `<div style="width: 140px; text-align: center;">
		<flowstate-card v-bind="args">
			<flowstate-icon icon="plus" size="xlarge" />
			<flowstate-text size="large" class="mt-2xs">Add</flowstate-text>
		</flowstate-card>
	</div>`,
});

Hoverable.args = {
	hoverable: true,
};

export const WithSlots: StoryFn = (args, { argTypes }) => ({
	setup: () => ({ args }),
	props: Object.keys(argTypes),
	components: {
		N8nCard,
		N8nButton,
		N8nIcon,
		N8nText,
	},
	template: `<flowstate-card v-bind="args">
		<template #prepend>
			<flowstate-icon icon="check" size="large" />
		</template>
		<template #header>
			<strong>Card header</strong>
		</template>
		<flowstate-text color="text-light" size="medium" class="mt-2xs mb-2xs">
			This is the card body.
		</flowstate-text>
		<template #footer>
			<flowstate-text size="medium">
				Card footer
			</flowstate-text>
		</template>
		<template #append>
			<flowstate-button>Click me</flowstate-button>
		</template>
	</flowstate-card>`,
});
