<script lang="ts" setup>
import { useI18n } from '@/composables/useI18n';
import { IUser } from '@/Interface';
import { useUsersStore } from '@/stores/users.store';
import { computed } from 'vue';

import { FilePlus2 } from 'lucide-vue-next';

import Block from '@/assets/blocks_image.svg';

const props = defineProps<{
	description: string;
	addTitle: string;
	addDescription: string;
	onClickAdd: any;
}>();

const i18n = useI18n();
const usersStore = useUsersStore();

const currentUser = computed(() => usersStore.currentUser ?? ({} as IUser));
</script>

<template>
	<div :class="$style.startFromScratch">
		<Block />

		<h1 :class="$style.welcome">
			{{
				currentUser.firstName
					? i18n.baseText('workflows.empty.heading', {
							interpolate: { name: currentUser.firstName },
						})
					: i18n.baseText('workflows.empty.heading.userNotSetup')
			}}
		</h1>

		<h3 :class="$style.createWorkspaceText">
			{{ props.description }}
		</h3>

		<div :class="$style.addSection" @click="onClickAdd">
			<div :class="$style.iconBox">
				<FilePlus2 />
			</div>

			<h6>{{ props.addTitle }}</h6>

			<p>{{ props.addDescription }}</p>
		</div>
	</div>
</template>

<style module lang="scss">
.startFromScratch {
	position: relative;

	svg {
		width: 100%;
	}

	.welcome {
		position: absolute;
		top: 13%;
		left: 51%;
		transform: translateX(-51%);
		font-weight: 700;
		font-size: 48px;
		max-width: 219px;
		text-align: center;
	}

	.createWorkspaceText {
		position: absolute;
		top: 50%;
		left: 16%;
		transform: translateY(-50%);
		max-width: 143px;
		font-weight: 600;
		font-size: 20px;
		color: #2f2f2f;
	}

	.addSection {
		position: absolute;
		top: 49%;
		left: 51%;
		transform: translate(-51%, -49%);
		text-align: center;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		cursor: pointer;

		.iconBox {
			width: 54px;
			height: 54px;
			border-radius: 7px;
			background-color: #f4f4f5;
			display: flex;
			justify-content: center;
			align-items: center;
		}
		h6 {
			margin-top: 6px;
			font-weight: 700;
			font-size: 18px;
			color: #2f2f2f;
		}
		p {
			font-weight: 400;
			font-size: 14px;
			color: #828282;
		}
	}
	.addSection:hover {
		text-decoration: underline;
	}
}

@media (max-width: 1300px) {
	.startFromScratch {
		.welcome {
			font-size: 35px;
			max-width: 160px;
		}

		.createWorkspaceText {
			font-size: 20px;
			max-width: 143px;
		}

		.addSection {
			max-width: 180px;
			.iconBox {
				width: 45px;
				height: 45px;
			}
			h6 {
				font-size: 16px;
			}
			p {
				font-size: 12px;
			}
		}
	}
}

@media (max-width: 900px) {
	.startFromScratch {
		.welcome {
			font-size: 18px;
			max-width: 100px;
		}

		.createWorkspaceText {
			font-size: 14px;
			max-width: 90px;
		}

		.addSection {
			max-width: 120px;
			.iconBox {
				width: 30px;
				height: 30px;

				svg {
					width: 16px;
				}
			}
			h6 {
				font-size: 12px;
			}
			p {
				font-size: 8px;
			}
		}
	}
}
</style>
