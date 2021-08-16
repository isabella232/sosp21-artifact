// +build !ignore_autogenerated

// Code generated by operator-sdk. DO NOT EDIT.

package v1

import (
	runtime "k8s.io/apimachinery/pkg/runtime"
)

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *YieldPolicy) DeepCopyInto(out *YieldPolicy) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ObjectMeta.DeepCopyInto(&out.ObjectMeta)
	out.Spec = in.Spec
	return
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new YieldPolicy.
func (in *YieldPolicy) DeepCopy() *YieldPolicy {
	if in == nil {
		return nil
	}
	out := new(YieldPolicy)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject is an autogenerated deepcopy function, copying the receiver, creating a new runtime.Object.
func (in *YieldPolicy) DeepCopyObject() runtime.Object {
	if c := in.DeepCopy(); c != nil {
		return c
	}
	return nil
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *YieldPolicyList) DeepCopyInto(out *YieldPolicyList) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ListMeta.DeepCopyInto(&out.ListMeta)
	if in.Items != nil {
		in, out := &in.Items, &out.Items
		*out = make([]YieldPolicy, len(*in))
		for i := range *in {
			(*in)[i].DeepCopyInto(&(*out)[i])
		}
	}
	return
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new YieldPolicyList.
func (in *YieldPolicyList) DeepCopy() *YieldPolicyList {
	if in == nil {
		return nil
	}
	out := new(YieldPolicyList)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject is an autogenerated deepcopy function, copying the receiver, creating a new runtime.Object.
func (in *YieldPolicyList) DeepCopyObject() runtime.Object {
	if c := in.DeepCopy(); c != nil {
		return c
	}
	return nil
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *YieldPolicySpec) DeepCopyInto(out *YieldPolicySpec) {
	*out = *in
	out.Source = in.Source
	out.Target = in.Target
	return
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new YieldPolicySpec.
func (in *YieldPolicySpec) DeepCopy() *YieldPolicySpec {
	if in == nil {
		return nil
	}
	out := new(YieldPolicySpec)
	in.DeepCopyInto(out)
	return out
}
