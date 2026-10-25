#!/usr/bin/env python3
# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""检查 Star Robot 的 PD 参数配置

运行此脚本查看当前 PD 参数和推荐值
运行: python check_pd_params.py
"""


def check_pd_configuration():
    """检查并显示 PD 参数配置"""

    print("=" * 80)
    print("🔍 Star Robot PD 参数检查")
    print("=" * 80)

    try:
        # 导入配置
        from isaaclab_assets import STAR_CFG

        print("\n✓ 成功加载机器人配置")

        # 显示执行器配置
        print("\n" + "=" * 80)
        print("⚙️  当前执行器配置:")
        print("=" * 80)

        for actuator_name, actuator_cfg in STAR_CFG.actuators.items():
            print(f"\n📌 执行器组: {actuator_name}")
            print(f"   关节匹配模式: {actuator_cfg.joint_names_expr}")
            print(f"   力矩限制: {actuator_cfg.effort_limit_sim} Nm")
            print(f"   刚度 (Stiffness): {actuator_cfg.stiffness}")
            print(f"   阻尼 (Damping): {actuator_cfg.damping}")

            # 计算阻尼比
            damping_ratio = actuator_cfg.damping / actuator_cfg.stiffness
            print(f"   阻尼比: {damping_ratio:.3f}")

            # 给出评估
            print("\n   评估:")
            if actuator_cfg.stiffness >= 400:
                print("   ✅ 刚度: 高 (适合减少抖动)")
            elif actuator_cfg.stiffness >= 200:
                print("   ⚠️  刚度: 中等 (可能有轻微抖动)")
            else:
                print("   ❌ 刚度: 低 (可能抖动严重)")

            if actuator_cfg.damping >= 40:
                print("   ✅ 阻尼: 高 (有效抑制震荡)")
            elif actuator_cfg.damping >= 20:
                print("   ⚠️  阻尼: 中等 (可能有震荡)")
            else:
                print("   ❌ 阻尼: 低 (可能震荡严重)")

            if 0.08 <= damping_ratio <= 0.12:
                print("   ✅ 阻尼比: 理想范围")
            else:
                print(f"   ⚠️  阻尼比: {damping_ratio:.3f} (建议: 0.08-0.12)")

        # 显示仿真参数
        print("\n" + "=" * 80)
        print("🔬 仿真求解器配置:")
        print("=" * 80)

        articulation_props = STAR_CFG.spawn.articulation_props
        print(f"\n位置迭代次数: {articulation_props.solver_position_iteration_count}")
        print(f"速度迭代次数: {articulation_props.solver_velocity_iteration_count}")

        if articulation_props.solver_position_iteration_count >= 12:
            print("✅ 位置迭代: 充足")
        elif articulation_props.solver_position_iteration_count >= 8:
            print("⚠️  位置迭代: 中等")
        else:
            print("❌ 位置迭代: 不足")

        if articulation_props.solver_velocity_iteration_count >= 1:
            print("✅ 速度迭代: 已启用")
        else:
            print("⚠️  速度迭代: 未启用")

        # 对比表
        print("\n" + "=" * 80)
        print("📊 参数对比表:")
        print("=" * 80)

        print("\n┌─────────────┬──────────┬──────────┬─────────────┐")
        print("│   参数      │   原值   │  当前值  │    推荐值   │")
        print("├─────────────┼──────────┼──────────┼─────────────┤")

        current_stiffness = list(STAR_CFG.actuators.values())[0].stiffness
        current_damping = list(STAR_CFG.actuators.values())[0].damping

        print(f"│ Stiffness   │   80.0   │ {current_stiffness:6.1f}   │  300-600    │")
        print(f"│ Damping     │    4.0   │ {current_damping:6.1f}   │   30-60     │")
        print(
            f"│ Pos Iter    │    8     │   {articulation_props.solver_position_iteration_count:2d}     │   12-16     │"
        )
        print(f"│ Vel Iter    │    0     │    {articulation_props.solver_velocity_iteration_count}     │    1-2      │")
        print("└─────────────┴──────────┴──────────┴─────────────┘")

        # 给出总体建议
        print("\n" + "=" * 80)
        print("💡 调优建议:")
        print("=" * 80)

        if current_stiffness >= 400 and current_damping >= 40:
            print("\n✅ 当前配置应该能显著减少抖动")
            print("   如果仍有抖动，尝试:")
            print("   1. 增加到 stiffness=600, damping=60")
            print("   2. 检查是否所有关节都被控制（无 '7 != 8' 警告）")
        elif current_stiffness >= 200:
            print("\n⚠️  当前配置中等，可能有轻微抖动")
            print("   建议增加到: stiffness=400, damping=40")
        else:
            print("\n❌ 当前配置过软，抖动可能严重")
            print("   强烈建议增加到: stiffness=400, damping=40")

        print("\n📚 详细调参指南请查看: PD_TUNING_GUIDE.md")

        # 检查关节配置
        print("\n" + "=" * 80)
        print("🔗 关节配置:")
        print("=" * 80)

        print(f"\n初始位置匹配模式: {list(STAR_CFG.init_state.joint_pos.keys())}")
        print(f"执行器匹配模式: {[cfg.joint_names_expr for cfg in STAR_CFG.actuators.values()]}")

        print("\n⚠️  重要: 确保关节匹配模式覆盖所有 8 个机械臂关节")
        print("   检查训练日志中是否有 '7 != 8' 警告")

        return True

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Star Robot PD 参数检查工具")
    print("=" * 80)
    print("\n此工具会显示:")
    print("  • 当前 PD 参数 (stiffness, damping)")
    print("  • 仿真求解器配置")
    print("  • 与推荐值的对比")
    print("  • 调优建议")
    print("\n")

    success = check_pd_configuration()

    if success:
        print("\n" + "=" * 80)
        print("✅ 检查完成")
        print("=" * 80)
        print("\n下一步:")
        print("  1. 如果需要调整参数，编辑: source/isaaclab_assets/.../robots/star.py")
        print("  2. 运行测试: python test_star_env.py")
        print("  3. 可视化验证: ./train_star_reach.sh --visual --num_envs 1")
        print("  4. 开始训练: ./train_star_reach.sh\n")

    exit(0 if success else 1)
